from functools import partial
from typing import Callable, Any
import numpy.typing as npt
from qualang_tools.results import fetching_tool
from qm import QuantumMachinesManager
from qm.qua import (
    program,
    update_frequency,
    Math,
    Cast,
    for_,
    stream_processing,
    declare,
    declare_stream,
    wait,
    measure,
    play,
    save,
    fixed,
    demod,
    declare_input_stream,
    advance_input_stream,
    amp,
    if_,
    else_,
    ramp_to_zero,
    while_,
    assign,
    infinite_loop_,
    FUNCTIONS,
    pause,
    align,
    ramp_to_zero,
)
from quam.core import QuamRoot, quam_dataclass
from quam.components import (
    SingleChannel,
    pulses,
    InOutSingleChannel,
    StickyChannelAddon,
)
from quam.components.virtual_gate_set import VirtualGateSet, VirtualPulse
from qualang_tools.loops import from_array
from typing import Dict, Union, List
from dataclasses import field


import numpy as np
from time import sleep
from abc import ABC, abstractmethod
from collections import defaultdict


class LiveMeasurement(ABC):
    @abstractmethod
    def start_acquisition(
        self,
    ): ...

    @abstractmethod
    def fetch_results(
        self,
    ): ...

    @abstractmethod
    def change_parameters(
        self,
    ): ...


@quam_dataclass
class QuAM(QuamRoot):
    gates: Dict[str, SingleChannel] = field(default_factory=dict)
    resonators: Dict[str, InOutSingleChannel] = field(default_factory=dict)
    VirtualGateSet1: VirtualGateSet = None
    VirtualGateSet2: VirtualGateSet = None

    def align_all(self):
        align(*self.resonators, *self.gates)


def make_quam(
    gates: Dict[str, int],
    virtual_gates: Dict[str, list] = None,
    resonator_input: int = 1,
    resonator_output: int = 1,
    resonator_freqs: Union[Dict[str, int], int] = 176553106,
    resonator_time_of_flight: int = 400,
    controller: str = "con1",
):
    """make a QuAM object for live plotting

    Args:
        gates (Dict[str, int]): gate_name, opx_output
        virtual_gates (Dict[str, list], optional): virtual_gate_name: list of virtualisation values (all gates required). Defaults to None.
        resonator_input (int, optional): Defaults to 1.
        resonator_output (int, optional): Defaults to 1.
        resonator_freq (int, optional): Hz.  Defaults to 176553106.
        resonator_time_of_flight (int, optional): ns. Defaults to 400.
        controller (str, optional): which opx config controller to set. Defaults to "con1".
    """

    # print("DIVIDERS SHOULD NOT BE APPLIED TO VIRTUAL GATES ALREADY!!!")
    machine = QuAM()
    machine.gates = {}
    for gate_name, opx_output in gates.items():
        add_gate_and_copy(machine, gate_name, opx_output, controller=controller)

    if virtual_gates is None:
        virt_matrix = np.eye(2, len(gates))
        virtual_gates = {
            f"virtual_gate_{i+1}": virt_matrix[i, :].tolist() for i in range(2)
        }

    assert len(virtual_gates) == 2, "only 2 virtual gates are supported"
    for virt_list in virtual_gates.values():
        assert len(virt_list) == len(
            gates
        ), "all gates must have a virtualisation value"

    machine.VirtualGateSet1 = VirtualGateSet(
        gates=[f"#/gates/{gate}" for gate in gates],  # Be careful with ordering
        virtual_gates=virtual_gates,
        pulse_defaults=[pulses.SquarePulse(amplitude=None, length=None) for _ in gates],
    )

    machine.VirtualGateSet2 = VirtualGateSet(
        gates=[f"#/gates/{gate}_copy" for gate in gates],  # Be careful with ordering
        virtual_gates=virtual_gates,
        pulse_defaults=[pulses.SquarePulse(amplitude=None, length=None) for _ in gates],
    )
    if isinstance(resonator_freqs, int):
        machine.resonators["resonator"] = InOutSingleChannel(
            id="resonator",
            opx_output=(controller, resonator_input),
            opx_input=(controller, resonator_output),
            intermediate_frequency=resonator_freqs,
            time_of_flight=resonator_time_of_flight,
        )
    elif isinstance(resonator_freqs, dict):
        for resonator_name, frequency in resonator_freqs.items():
            machine.resonators[resonator_name] = InOutSingleChannel(
                id=resonator_name,
                opx_output=(controller, resonator_input),
                opx_input=(controller, resonator_output),
                intermediate_frequency=frequency,
                time_of_flight=resonator_time_of_flight,
            )
    return machine


def add_gate_and_copy(machine, gate_name, opx_output, controller):
    machine.gates[gate_name] = SingleChannel(
        id=gate_name,
        opx_output=(controller, opx_output),
        sticky=StickyChannelAddon(duration=200, digital=False),
    )
    machine.gates[gate_name + "_copy"] = SingleChannel(
        id=gate_name + "_copy",
        opx_output=(controller, opx_output),
        sticky=StickyChannelAddon(duration=200, digital=False),
    )
    return machine


class VirtualGateSetMeasurement:
    def __init__(
        self,
        qmm: QuantumMachinesManager,
        QuAM: QuAM,
        resolution: int,
        readout_time_us: int,
        readout_amplitude: float,
        dividers: Dict[str, float],
        integration_weights_angle: Dict[str, float] = None,
        scan_range: float = 0.05,
        buffer_time_ns: int = 100,
        opx_repetitions: int = 100,
        make_program: bool = True,
        save_all: bool = False,
    ):
        # TODO: move everything related to creating the quam object to the QuAM class
        print("DIVIDERS SHOULD NOT BE APPLIED TO VIRTUAL GATES ALREADY!!!")
        self.readout_time_ns = int(readout_time_us * 1e3)
        self.readout_time_clk = int(self.readout_time_ns // 4)
        self.resolution = resolution
        self.quam = QuAM
        self._scan_range = scan_range
        self.buffer_time_ns = int(buffer_time_ns)
        self.buffer_time_clk = int(buffer_time_ns // 4)
        self.opx_repetitions = opx_repetitions
        self.dividers = dividers
        self.qmm = qmm

        for gate in self.quam.gates.values():
            assert gate.sticky, f"{gate} is not sticky, this is required for this class"

        self.setup_resonators(readout_amplitude, integration_weights_angle)
        self.setup_slow_gateset(self.quam.VirtualGateSet1)
        self.setup_fast_gateset(self.quam.VirtualGateSet2)

        self.update = False
        self.virtual_gate_names = np.array(
            list(self.quam.VirtualGateSet1.virtual_gates.keys())
        )
        self.gate_names = np.array(
            [gate_name for gate_name in self.quam.gates if "copy" not in gate_name]
        )
        self.virtual_matrix = np.array(
            list(self.quam.VirtualGateSet1.virtual_gates.values()), dtype=float
        ).T
        assert (
            self.virtual_matrix
            == np.array(list(self.quam.VirtualGateSet2.virtual_gates.values())).T
        ).all(), "all virtual gates must match"

        self.make_virtual_setters_and_getters()

        if make_program:
            self.config = self.quam.generate_config()
            self.program = self.make_program(save_all=save_all)
            self.qm = self.qmm.open_qm(self.config)
            self.program_id = self.qm.compile(self.program)

    # setters and getters are needed for qcodes integration
    def make_virtual_setters_and_getters(
        self,
    ):
        self.virtual_setters = {}
        self.virtual_getters = {}

        for virt_index, virt in enumerate(self.virtual_gate_names):
            for gate_index, gate in enumerate(self.gate_names):
                self.virtual_setters[f"{virt}_to_{gate}"] = partial(
                    self.set_virt_element, virt_index=virt_index, gate_index=gate_index
                )
                self.virtual_getters[f"{virt}_to_{gate}"] = partial(
                    self.get_virt_element, virt_index=virt_index, gate_index=gate_index
                )

    def scan_range_getter(
        self,
    ):
        return self._scan_range

    def scan_range_setter(self, value):
        self.update = True
        self._scan_range = value

    def set_virt_element(self, value, virt_index, gate_index):
        self.update = True
        self.virtual_matrix[gate_index, virt_index] = value

    def get_virt_element(self, virt_index, gate_index):
        return self.virtual_matrix[gate_index, virt_index]

    # sets up pulses in the config using quam
    def setup_resonators(self, readout_amplitude, integration_weights_angle):
        if integration_weights_angle is None:
            integration_weights_angle = defaultdict(lambda: 0)
        for resonator in self.quam.resonators.values():
            resonator.operations["readout"] = pulses.ConstantReadoutPulse(
                length=self.readout_time_ns,
                amplitude=readout_amplitude,
                integration_weights_angle=integration_weights_angle[resonator.id],
            )

    # TODO: for different cuts in same live plot, add "prefix" argument here and generate multiple
    # operations, 1 set for each cut
    def setup_slow_gateset(self, virtual_gate_set):
        virtual_gate_set.operations["slow_pulse"] = VirtualPulse(
            length=int(self.readout_time_ns + self.buffer_time_ns),
            amplitudes={
                list(virtual_gate_set.virtual_gates.keys())[0]: self._scan_range
            },
        )

    def setup_fast_gateset(self, virtual_gate_set):
        virtual_gate_set.operations["big_pulse"] = VirtualPulse(
            length=int(self.readout_time_ns + self.buffer_time_ns),
            amplitudes={
                list(virtual_gate_set.virtual_gates.keys())[
                    1
                ]: -self._scan_range  # minus important here
            },
        )
        virtual_gate_set.operations["small_pulse"] = VirtualPulse(
            length=int(self.readout_time_ns + self.buffer_time_ns),
            amplitudes={
                list(virtual_gate_set.virtual_gates.keys())[1]: (self._scan_range * 2)
                / (self.resolution - 1)
            },
        )

    def make_program(
        self,
        save_all,
    ):
        """makes program for live_plotting,

        Args:
            save_all (bool): whether to save all acquired data for the livestream (only used in testing)

        Returns:
            prog: qua program
        """
        with program() as prog:
            repetition_counter = declare(int)
            streams = [
                (declare_stream(), declare_stream())
                for resonator in self.quam.resonators
            ]
            # I_stream = declare_stream()
            # Q_stream = declare_stream()

            with infinite_loop_():
                with for_(*from_array(repetition_counter, range(self.opx_repetitions))):
                    self.do_one_map(streams)
                    wait(1000)
                pause()

            with stream_processing():
                for I_streamQ_stream, resonator in zip(streams, self.quam.resonators):
                    I_stream, Q_stream = I_streamQ_stream
                    I_stream.buffer(
                        self.opx_repetitions, self.resolution, self.resolution
                    ).map(FUNCTIONS.average(0)).save(f"I_{resonator}")
                    Q_stream.buffer(
                        self.opx_repetitions, self.resolution, self.resolution
                    ).map(FUNCTIONS.average(0)).save(f"Q_{resonator}")

                    if save_all:
                        I_stream.buffer(
                            self.opx_repetitions, self.resolution, self.resolution
                        ).map(FUNCTIONS.average(0)).save_all("I_full")
                        Q_stream.buffer(
                            self.opx_repetitions, self.resolution, self.resolution
                        ).map(FUNCTIONS.average(0)).save_all("Q_full")

        return prog

    # TODO: add "prefix" argument, to choose which cut is being run
    def do_one_map(self, streams):
        """macro for doing one map

        Args:
            streams (list[quaStreams]): I/Q streams for each resonator
        """
        amplitude_scale_slow = declare(fixed)
        small_jumps = declare(int)
        with for_(
            *from_array(amplitude_scale_slow, np.linspace(-1, 1, self.resolution))
        ):

            self.quam.align_all()
            self.quam.VirtualGateSet1.play("slow_pulse", amplitude_scale_slow)

            self.quam.VirtualGateSet2.play(
                "big_pulse",
            )
            self._measurement_macro(streams=streams)

            with for_(*from_array(small_jumps, range(self.resolution - 1))):
                self.quam.VirtualGateSet2.play(
                    "small_pulse",
                )
                self._measurement_macro(streams=streams)

            for gate in self.quam.gates:
                ramp_to_zero(gate, duration=1)

            # Do correction

            self.quam.VirtualGateSet1.play("slow_pulse", -1 * amplitude_scale_slow)
            self.quam.VirtualGateSet2.play("big_pulse", -1)

            with for_(*from_array(small_jumps, range(self.resolution - 1))):
                self.quam.VirtualGateSet2.play("small_pulse", amplitude_scale=-1)

            self.quam.align_all()
            for gate in self.quam.gates:
                ramp_to_zero(gate, duration=1)

            wait(100)

    def _measurement_macro(self, streams: List[tuple]):
        wait(self.buffer_time_clk, *self.quam.resonators)
        # each resonator needs an I and Q stream
        for I_streamQ_stream, resonator in zip(streams, self.quam.resonators.values()):
            I_stream, Q_stream = I_streamQ_stream
            i_var, q_var = resonator.measure("readout")
            save(i_var, I_stream)
            save(q_var, Q_stream)

    def get_overrides_from_virtual_matrix(self, virtual_matrix):
        """
        get waveform overrides from virtual matrix for qua add_compiled
        also applies dividers
        Args:
            virtual_matrix (np.ndarray)

        Returns:
            dict: overrides for add_compiled
        """
        gate_vals_slow = virtual_matrix @ np.array([self._scan_range, 0])
        gate_vals_fast = virtual_matrix @ np.array([0, self._scan_range])

        overrides = {"waveforms": {}}

        for i, gate in enumerate(self.quam.VirtualGateSet1.gates):
            overrides["waveforms"][f"{gate.id}.slow_pulse.wf"] = (
                gate_vals_slow[i] * self.dividers[gate.id]
            )

        for i, gate in enumerate(self.quam.VirtualGateSet2.gates):
            overrides["waveforms"][f"{gate.id}.big_pulse.wf"] = (
                -gate_vals_fast[i] * self.dividers[gate.id]
            )
            overrides["waveforms"][f"{gate.id}.small_pulse.wf"] = (
                gate_vals_fast[i] * 2 / (self.resolution - 1) * self.dividers[gate.id]
            )

        return overrides

    def start_acquisition(self, overrides=None):
        """starts qua program and data fetching
        this function is both used at the start of live plotting and every time
        something in the program needs to be updated
        Args:
            overrides (dict, optional): overrides for add_compiled. Defaults to None.
        """
        if hasattr(self, "job"):
            self.job.halt()
            self.job = self._add_compiled(overrides=overrides)

        else:
            self.job = self._add_compiled(
                overrides=self.get_overrides_from_virtual_matrix(self.virtual_matrix)
            )

        sleep(3)
        data_list = []
        for resonator in self.quam.resonators:
            data_list.extend([f"I_{resonator}", f"Q_{resonator}"])

        self.data_fetcher = fetching_tool(
            self.job,
            data_list=data_list,
            mode="live",
        )

    def fetch_results(self, live_plot=True):
        if hasattr(self, "data_fetcher"):
            pass
        else:
            raise Exception(
                'data fetcher not started, run "start_measurement" before trying to fetch results'
            )

        while not self.job.is_paused():
            sleep(0.01)

        all_data = self.data_fetcher.fetch_all()
        I = all_data[0]  # TODO: this should be made more general
        Q = all_data[1]
        I2 = all_data[2]
        if self.update:
            overrides = self.get_overrides_from_virtual_matrix(self.virtual_matrix)
            self.start_acquisition(overrides=overrides)
            self.update = False
        else:
            self.job.resume()

        if live_plot:
            return np.array(
                [I, I2]
            )  # this has to be np.array class to pass the validator of the qcodes parameters in the instruement
        else:
            return (
                I,
                Q,
            )  # I.reshape(self.resolution, self.resolution), Q.reshape(self.resolution, self.resolution)

    def _add_compiled(self, overrides=None):
        pending_job = self.qm.queue.add_compiled(self.program_id, overrides=overrides)
        return pending_job.wait_for_execution()


class VirtualGateSetMeasurementBetter(VirtualGateSetMeasurement):
    def do_one_map(self, I_stream, Q_stream):

        amplitude_scale_slow = declare(fixed)
        # small_jumps = declare(int)
        with for_(
            *from_array(
                amplitude_scale_slow,
                np.linspace(-1, 1, self.resolution)[: self.resolution // 2],
            )
        ):

            self.do_one_row(amplitude_scale_slow, I_stream, Q_stream)

            # Do correction

            self.do_one_row(-1 * amplitude_scale_slow, I_stream, Q_stream)

            wait(100)

        assign(amplitude_scale_slow, 0)
        self.do_one_row(amplitude_scale_slow, I_stream, Q_stream)

    def do_one_row(
        self,
        amplitude_scale,
        I_stream,
        Q_stream,
    ):
        small_jumps = declare(int)
        self.quam.align_all()
        self.quam.VirtualGateSet1.play("slow_pulse", amplitude_scale)

        self.quam.VirtualGateSet2.play(
            "big_pulse",
        )
        wait(self.buffer_time_clk)
        i_var, q_var = self.quam.resonator.measure("readout")
        save(i_var, I_stream)
        save(q_var, Q_stream)

        with for_(*from_array(small_jumps, range(self.resolution - 1))):
            self.quam.VirtualGateSet2.play(
                "small_pulse",
            )
            wait(self.buffer_time_clk, self.quam.resonator.id)
            i_var, q_var = self.quam.resonator.measure("readout")
            save(i_var, I_stream)
            save(q_var, Q_stream)

        for gate in self.quam.gates:
            ramp_to_zero(gate, duration=1)

    def fetch_results(self, live_plot=True):
        returns = super().fetch_results(live_plot=live_plot)
        if live_plot:
            i = returns
            return self.reorder_rows(i)
        else:
            i, q = returns
            return self.reorder_rows(i), self.reorder_rows(q)

    def reorder_rows(self, arr):
        rows_even = arr[::2]
        rows_odd = arr[1::2]

        return np.concatenate([rows_even, rows_odd[::-1]])


def spiral_order(N: int):
    # casting to int if necessary
    if not isinstance(N, int):
        N = int(N)
    # asserting that N is odd
    N = N if N % 2 == 1 else N + 1

    # setting i, j to be in the middle of the image
    i, j = (N - 1) // 2, (N - 1) // 2

    # creating array to hold the ordering
    order = np.zeros(shape=(N, N), dtype=int)

    sign = +1  # the direction which to move along the respective axis
    number_of_moves = 1  # the number of moves needed for the current edge
    total_moves = 0  # the total number of moves completed so far

    # spiralling outwards along x edge then y
    while total_moves < N**2 - N:
        for _ in range(number_of_moves):
            i = i + sign  # move one step in left (sign = -1) or right (sign = +1)
            total_moves = total_moves + 1
            order[i, j] = total_moves  # updating the ordering array

        for _ in range(number_of_moves):
            j = j + sign  # move one step in down (sign = -1) or up (sign = +1)
            total_moves = total_moves + 1
            order[i, j] = total_moves
        sign = sign * -1  # the next moves will be in the opposite direction
        number_of_moves = (
            number_of_moves + 1
        )  # the next edges will require one more step

    # filling the final x edge, which cannot cleanly be done in the above while loop
    for _ in range(number_of_moves - 1):
        i = i + sign  # move one step in left (sign = -1) or right (sign = +1)
        total_moves = total_moves + 1
        order[i, j] = total_moves

    return order


class OPX_live_controller:
    """
    Modified from: https://github.com/qua-platform/qua-libs/tree/main/Quantum-Control-Applications/Quantum-Dots/Use%20Case%201%20-%20Fast%202D%20Scans
    """

    def __init__(
        self,
        elements,  #: tuple[str, ...],
        virtual_ranges,  #: tuple[float, ...],
        resolution: int,
        qm,
        readout_pulse: str,
        config: Any,
        extra_step=None,
        extra_step_after_measurement=None,
        n_averages: int = 20,
        virtualization_matrix=None,
        wait_time: float = 0,
        jump_pulse: str = "CW",
        measured_element: str = "bottom_left_DQD_readout",
        dividers={
            "gate_41": 7.9,
            "gate_46": 8.1,
        },  #: dict[str, float] = {"gate_41": 7.9, "gate_46": 8.1},
        perform_measurement: bool = True,
        run_test: bool = False,
    ):
        assert len(dividers) == len(
            elements
        ), f"Each element must have an associated divider, {len(elements)} elements were given with {len(dividers)}"
        assert elements == list(
            dividers.keys()
        ), "elements and dividers must be given in same order, could be fixed later."

        self.qm = qm
        if (np.array(virtual_ranges) > 0.5).any():
            raise Exception(
                f"Virtual ranges must be given in units of Volt, values above 0.5 will raise this error, values given were:{virtual_ranges}"
            )

        if extra_step is not None:
            self.extra_step = extra_step

        if extra_step_after_measurement is not None:
            self.extra_step_after_measurement = extra_step_after_measurement

        if (extra_step is not None) != (extra_step_after_measurement is not None):
            print(
                "WARNING: if extra_step is provided, it is strongly adviced to also provide extra_step_after measurement to compensate."
            )

        # get length of readout pulse, likely not need as time will be set by measurement anyway (possibly only with aligns)
        self.readout_pulse_length = (
            config["pulses"][readout_pulse]["length"] // 4
        )  # length in clockcycles
        self.readout_pulse = readout_pulse
        self.set_resolution(resolution)

        # get jump pulse and jump pulse amplitude, will be used to output correct voltages
        self.jump_pulse = jump_pulse
        CW_pulse = config["pulses"][jump_pulse]["waveforms"]["single"]
        self.jump_amp = config["waveforms"][CW_pulse]["sample"]

        self.measured_element = measured_element
        self.elements = elements
        self.virtual_ranges = list(virtual_ranges)
        self._virtual_ranges_converted = np.array([0.0, 0.0])

        # self.set_virtual1_range(virtual_ranges[0])
        # self.set_virtual2_range(virtual_ranges[1])

        if virtualization_matrix is None:
            self.virtualization_matrix = np.eye(2, len(elements))
        else:
            self.virtualization_matrix = virtualization_matrix
            assert virtualization_matrix.shape == (
                2,
                len(elements),
            ), f"wrong shape of virtualization matrix, expected {(2,len(elements))} got {virtualization_matrix.shape}"

        self.dividers = dividers
        self.apply_dividers()
        self.wait_time = wait_time

        self.set_virtual1_range(virtual_ranges[0])
        self.set_virtual2_range(virtual_ranges[1])

        self.n_averages = n_averages
        self.update = True
        self.perform_measurement = perform_measurement  # only for testing
        self.run_test = run_test  # only for testing

        # print("virt_matrix", self.virtualization_and_dividers_matrix)
        # step_size_matrix = np.zeros(self.virtualization_and_dividers_matrix.shape)
        self.update_outside_step_size_matrix()

        self.program = self.make_program()

        self.virtual_setters = self.make_virt_setters(
            ("virtual1", "virtual2"), elements
        )
        self.virtual_getters = self.make_virt_getters(
            ("virtual1", "virtual2"), elements
        )

        self._perform_extra_step = False

    @property
    def perform_extra_step(
        self,
    ):
        return self._perform_extra_step

    @perform_extra_step.setter
    def perform_extra_step(self, value):
        self.update = True
        self._perform_extra_step = value

    def set_virt_element(self, value: float, virtual_index: int, element: int) -> None:
        self.virtualization_matrix[virtual_index, element] = value
        self.apply_dividers()
        # self.update_outside_step_size_matrix()
        self.update = True

    def get_virt_element(self, virtual_index: int, element: int) -> float:
        return self.virtualization_matrix[virtual_index, element]

    def apply_dividers(
        self,
    ):
        self.virtualization_and_dividers_matrix = (
            self.virtualization_matrix
            * np.array(list(self.dividers.values()))[np.newaxis, :]
        )

    def make_virt_setters(
        self,
        virtual_gates,  #: tuple[str, ...],
        elements,  #: tuple[str, ...]
    ):  # -> dict[str, partial[None]]:
        virtual_setters = {}
        for i, virt in enumerate(virtual_gates):
            for j, element in enumerate(elements):
                virtual_setters[f"{element}_{virt}"] = partial(
                    self.set_virt_element, virtual_index=i, element=j
                )  # lambda x: self.set_virt_element(
        return virtual_setters

    def make_virt_getters(
        self,
        virtual_gates,  #: tuple[str, ...],
        elements,  #: tuple[str, ...]
    ):  # -> dict[str, partial[None]]:
        virtual_getters = {}
        for i, virt in enumerate(virtual_gates):
            for j, element in enumerate(elements):
                virtual_getters[f"{element}_{virt}"] = partial(
                    self.get_virt_element, virtual_index=i, element=j
                )  # lambda x: self.set_virt_element(
        return virtual_getters

    def set_virtual1_range(self, value: float) -> None:
        # print("virt1", value)
        self.virtual_ranges[0] = value
        # print(self.virtual_ranges[0])
        # print(self.jump_amp)
        self._virtual_ranges_converted[0] = value / self.jump_amp
        # print("virt1", self._virtual_ranges_converted)
        # self.update_outside_step_size_matrix()
        self.update = True

    def set_virtual2_range(self, value: float) -> None:
        self.virtual_ranges[1] = value
        self._virtual_ranges_converted[1] = value / self.jump_amp
        # self.update_outside_step_size_matrix()
        self.update = True

    def set_resolution(self, value: float) -> None:
        assert value % 2 == 1, "the resolution must be odd {}".format(value)
        self.resolution = int(value)
        self.update = True

    def update_outside_step_size_matrix(
        self,
    ):
        step_sizes = self._virtual_ranges_converted / (self.resolution - 1)
        # print("step sized", step_sizes)
        self.outside_step_size_matrix = (
            self.virtualization_and_dividers_matrix * np.array(step_sizes).T
        )
        self.update = True
        # print("outside_step_matrix", self.outside_step_size_matrix)

    def measurement_macro(
        self,
    ):
        if not self.perform_measurement:
            pass

        if self.wait_time >= 4:  # if logic to enable wait_time = 0 without error
            wait(self.wait_time, self.measured_element)

        measure(
            self.readout_pulse,
            self.measured_element,
            None,
            demod.full("cos", self._I),
            demod.full("sin", self._Q),
        )
        wait(int(self.readout_pulse_length), *self.elements)

        save(self._I, self._I_stream)
        save(self._Q, self._Q_stream)

        # if self.wait_time >= 4:  # if logic to enable wait_time = 0 without error
        #     wait(self.wait_time)

    def extra_steps_and_measurement(self, extra_step_input_stream):
        with if_(extra_step_input_stream):
            self.extra_step()
            self.measurement_macro()
            self.extra_step_after_measurement()
        with else_():
            self.measurement_macro()

    def extra_step(
        self,
    ):
        pass

    def extra_step_after_measurement(
        self,
    ):
        pass

    def make_program(
        self,
    ):
        ramp_to_zero_duration = 1
        if self.n_averages == 0:
            repeats = 1
        else:
            repeats = self.n_averages

        with program() as spiral_scan:
            update_input_stream = declare_input_stream(bool, name="update_input_stream")
            extra_step_input_stream = declare_input_stream(
                bool, name="extra_step_input_stream"
            )
            step_size_matrix_input_stream = declare_input_stream(
                fixed, name="step_size_matrix_input_stream", size=len(self.elements) * 2
            )

            step_size_matrix = np.array(
                [[declare(fixed) for i in range(len(self.elements))] for j in range(2)]
            )

            i = declare(int)  # an index variable for the x index
            j = declare(int)  # an index variable for the y index
            average_index = declare(int)

            self.gate_vals = {gate: declare(fixed, value=0) for gate in self.elements}
            self.gate_vals_streams = {gate: declare_stream() for gate in self.elements}

            # virtualization_stream = declare_stream()
            step_size_stream = declare_stream()
            moves_per_edge = declare(
                int
            )  # the number of moves per edge [1, resolution]
            completed_moves = declare(
                int
            )  # the number of completed move [0, resolution ** 2]
            movement_direction = declare(fixed)  # which direction to move {-1., 1.}

            # declaring the measured variables and their streams
            self._I, self._Q = declare(fixed), declare(fixed)
            self._I_stream, self._Q_stream = declare_stream(), declare_stream()

            with infinite_loop_():
                if self.run_test:
                    raise Exception("run_test needs to be reimplemented")
                    # assign(
                    #     virtual_steps[0],
                    #     self._virtual_ranges_converted[0] * div_resolution,
                    # )
                    # assign(
                    #     virtual_steps[1],
                    #     self._virtual_ranges_converted[1] * div_resolution,
                    # )
                    # # print('ranges*div',self.virtual_ranges[0]*div_resolution, self.virtual_ranges[1]*div_resolution)

                    # for k in range(2):
                    #     for l in range(len(self.elements)):
                    #         assign(
                    #             step_size_matrix[k, l],
                    #             self.virtualization_and_dividers_matrix[k, l]
                    #             * virtual_steps[k],
                    #         )
                    #         # print(k, self.elements[l], self.virtualization_and_dividers_matrix[k,l] * self.virtual_ranges[k]*div_resolution )
                else:
                    advance_input_stream(update_input_stream)
                    with if_(update_input_stream):
                        advance_input_stream(step_size_matrix_input_stream)
                        advance_input_stream(extra_step_input_stream)
                        for k in range(2):
                            for l in range(len(self.elements)):
                                assign(
                                    step_size_matrix[k, l],
                                    step_size_matrix_input_stream[
                                        k * len(self.elements) + l
                                    ],
                                )

                        for thing in step_size_matrix.flatten():
                            save(thing, step_size_stream)

                with for_(average_index, 0, average_index < repeats, average_index + 1):
                    assign(moves_per_edge, 1)
                    assign(completed_moves, 0)
                    assign(movement_direction, 1)

                    # for the first pixel it is unnecessary to move before measuring
                    for gate in self.elements:
                        assign(self.gate_vals[gate], 0)
                        save(self.gate_vals[gate], self.gate_vals_streams[gate])

                    self.extra_steps_and_measurement(extra_step_input_stream)

                    with while_(
                        completed_moves < self.resolution * (self.resolution - 1)
                    ):
                        align(self.measured_element, *self.elements)
                        # for_ loop to move the required number of moves in the x direction
                        with for_(i, 0, i < moves_per_edge, i + 1):
                            self._step_gates(step_size_matrix[0, :], movement_direction)
                            self.extra_steps_and_measurement(extra_step_input_stream)

                        # for_ loop to move the required number of moves in the y direction
                        with for_(j, 0, j < moves_per_edge, j + 1):
                            self._step_gates(step_size_matrix[1, :], movement_direction)
                            self.extra_steps_and_measurement(extra_step_input_stream)

                        # updating the variables
                        assign(
                            completed_moves, completed_moves + 2 * moves_per_edge
                        )  # * 2 because moves in both x and y
                        assign(
                            movement_direction, movement_direction * -1
                        )  # *-1 as subsequent steps in the opposite direction
                        assign(
                            moves_per_edge, moves_per_edge + 1
                        )  # moving one row/column out so need one more move_per_edge

                    # filling in the final x row, which was not covered by the previous for_ loop
                    with for_(i, 0, i < moves_per_edge - 1, i + 1):
                        self._step_gates(step_size_matrix[0, :], movement_direction)
                        # Make sure that we measure after the pulse has settled
                        self.extra_steps_and_measurement(extra_step_input_stream)

                    # aligning and ramping to zero to return to initial state
                    for gate in self.elements:
                        ramp_to_zero(gate, duration=ramp_to_zero_duration)

                    wait(200)  # this wait is not needed
                pause()

            with stream_processing():
                if self.perform_measurement:
                    for stream_name, stream in zip(
                        ["I", "Q"], [self._I_stream, self._Q_stream]
                    ):
                        if self.n_averages == 0:
                            stream.buffer(self.resolution**2).save(stream_name)
                        else:
                            stream.buffer(repeats, self.resolution**2).map(
                                FUNCTIONS.average(0)
                            ).save(stream_name)
                for gate, stream in self.gate_vals_streams.items():
                    stream.buffer(self.resolution**2).save_all(gate)

                step_size_stream.buffer(*step_size_matrix.shape).save_all("step_size")

        return spiral_scan

    def _step_gates(self, step_size_list, movement_direction):
        for gate, step_size in zip(self.elements, step_size_list):
            play(
                "CW" * amp(movement_direction * step_size),
                gate,
                duration=self.readout_pulse_length,
            )
            assign(
                self.gate_vals[gate],
                self.gate_vals[gate] + self.jump_amp * (movement_direction * step_size),
            )
            save(self.gate_vals[gate], self.gate_vals_streams[gate])

    def send_input_streams(
        self,
    ):
        self.running_job.insert_input_stream("update_input_stream", [True])

        self.update_outside_step_size_matrix()

        self.running_job.insert_input_stream(
            "step_size_matrix_input_stream",
            self.outside_step_size_matrix.flatten().tolist(),
        )

        self.running_job.insert_input_stream(
            "extra_step_input_stream", [self._perform_extra_step]
        )

    def start_measurement(
        self,
    ):
        self.running_job = self.qm.execute(self.program)
        self.send_input_streams()

        sleep(3)

        self.data_fetcher = fetching_tool(
            self.running_job,
            data_list=[
                "I",
                "Q",
            ],
            mode="live",
        )
        print("REMEMBER TO END MEASUREMENT")

    def convert_gate_vals_to_device_voltage(self, gate_vals, divider):
        return gate_vals * self.jump_amp / divider

    def fetch_results(
        self,
    ):
        if hasattr(self, "data_fetcher"):
            pass
        else:
            raise Exception(
                'data fetcher not started, run "start_measurement" before trying to fetch results'
            )

        while not self.running_job.is_paused():
            sleep(0.01)

        if self.update:
            self.send_input_streams()
            self.update = False
        else:
            self.running_job.insert_input_stream("update_input_stream", [False])

        I, Q = self.data_fetcher.fetch_all()
        self.running_job.resume()
        amplitude = I**2 + Q**2
        self.order = spiral_order(self.resolution)
        return amplitude[self.order]

    def end_measurement(
        self,
    ):
        print(f"program ended: {self.running_job.halt()}")
