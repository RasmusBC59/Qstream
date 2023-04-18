from qualang_tools.results import fetching_tool
from qm.qua import (
    wait_for_trigger,
    reset_phase,
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
    ramp,
    amp,
    if_,
    elif_,
    else_,
    align,
    ramp_to_zero,
    while_,
    pause,
    assign,
    IO1,
    infinite_loop_,
)
import numpy as np
from macros import round_to_fixed, spiral_order
from time import sleep

accepted_modes = ["average", "latest", "all"]


class Live_plotting_spiral_modifiable:
    """
    Modified from: https://github.com/qua-platform/qua-libs/tree/main/Quantum-Control-Applications/Quantum-Dots/Use%20Case%201%20-%20Fast%202D%20Scans
    """

    def __init__(
        self,
        gate1,
        gate1_range,
        gate2,
        gate2_range,
        resolution,
        qm,
        readout_pulse,
        config,
        measured_element="bottom_left_DQD_readout",
        dividers={"gate_41": 7.9 * 1e-3, "gate_46": 8.1 * 1e-3},
    ):
        self.qm = qm
        self.readout_pulse_length = (
            config["pulses"][readout_pulse]["length"] // 4
        )  # length in clockcycles
        self.readout_pulse = readout_pulse
        self.CW_amp = config["waveforms"]["const_wf"]["sample"]
        self.measured_element = measured_element

        self.gate1 = gate1
        self.gate2 = gate2
        self.dividers = dividers

        self.set_resolution(resolution)
        self.set_gate1_range(gate1_range)
        self.set_gate2_range(gate2_range)

        self.update = True
        self.program = self.make_spiral_program_modifiable(resolution)

    def set_gate1_range(self, value):
        self.gate1_range = value * self.dividers[self.gate1] / self.CW_amp
        self.update = True

    def set_gate2_range(self, value):
        self.gate2_range = value * self.dividers[self.gate2] / self.CW_amp
        self.update = True

    def set_resolution(self, value):
        assert value % 2 == 1, "the resolution must be odd {}".format(value)
        self.resolution = int(value)
        self.update = True

    def measurement_macro(self, I, Q, I_stream, Q_stream):
        measure(
            self.readout_pulse,
            self.measured_element,
            None,
            demod.full("cos", I),
            demod.full("sin", Q),
        )
        save(I, I_stream)
        save(Q, Q_stream)

    def make_spiral_program_modifiable(self, resolution):  # resolution, x_amp, y_amp):
        # assert resolution % 2 == 1, "the resolution must be odd {}".format(resolution)

        # x_step_size = round_to_fixed(x_amp / (resolution - 1) / self.CW_amp)
        # y_step_size = round_to_fixed(y_amp / (resolution - 1) / self.CW_amp)

        # Perturbation parameters
        ramp_to_zero_duration = 1
        wait_time = 0
        div_resolution = 1 / (self.resolution - 1)

        with program() as spiral_scan:
            # resolution_input_stream = declare_input_stream(int, name='resolution_input_stream')
            ranges_input_stream = declare_input_stream(
                fixed, name="ranges_input_stream", size=2
            )
            update_input_stream = declare_input_stream(bool, name="update_input_stream")

            x_step_size = declare(fixed)
            y_step_size = declare(fixed)
            # resolution = declare(int)
            # div_resolution = declare(fixed)

            i = declare(int)  # an index variable for the x index
            j = declare(int)  # an index variable for the y index

            x = declare(fixed)  # a variable to keep track of the x coordinate
            y = declare(fixed)  # a variable to keep track of the x coordinate
            x_st = declare_stream()
            y_st = declare_stream()
            moves_per_edge = declare(
                int
            )  # the number of moves per edge [1, resolution]
            completed_moves = declare(
                int
            )  # the number of completed move [0, resolution ** 2]
            movement_direction = declare(fixed)  # which direction to move {-1., 1.}

            # declaring the measured variables and their streams
            I, Q = declare(fixed), declare(fixed)
            I_stream, Q_stream = declare_stream(), declare_stream()

            with infinite_loop_():
                # collect the resolution and xranges
                advance_input_stream(update_input_stream)
                with if_(update_input_stream):
                    # advance_input_stream(resolution_input_stream)
                    advance_input_stream(ranges_input_stream)

                    # assign(resolution, resolution_input_stream)
                    # assign(div_resolution, Math.div(1, resolution-1))
                    assign(x_step_size, ranges_input_stream[0] * div_resolution)
                    assign(y_step_size, ranges_input_stream[1] * div_resolution)
                save(x_step_size, x_st)
                save(y_step_size, y_st)

                # initialising variables
                assign(moves_per_edge, 1)
                assign(completed_moves, 0)
                assign(movement_direction, +1)

                # assign(x, 0.0)
                # assign(y, 0.0)
                # save(x, x_st)
                # save(y, y_st)
                # for the first pixel it is unnecessary to move before measuring

                self.measurement_macro(
                    I=I,
                    I_stream=I_stream,
                    Q=Q,
                    Q_stream=Q_stream,
                )

                with while_(completed_moves < resolution * (resolution - 1)):
                    # for_ loop to move the required number of moves in the x direction
                    with for_(i, 0, i < moves_per_edge, i + 1):
                        assign(x, x + movement_direction * x_step_size * 0.25)
                        # save(x, x_st)
                        # save(y, y_st)
                        # if the x coordinate should be 0, ramp to zero to remove fixed point arithmetic errors accumulating
                        with if_(x == 0.0):
                            ramp_to_zero(self.gate1, duration=ramp_to_zero_duration)
                        # playing the constant pulse to move to the next pixel
                        with else_():
                            play(
                                "CW" * amp(movement_direction * x_step_size), self.gate1
                            )

                        # Make sure that we measure after the pulse has settled
                        align(self.gate1, self.gate2, self.measured_element)
                        if (
                            wait_time >= 4
                        ):  # if logic to enable wait_time = 0 without error
                            wait(wait_time, self.measured_element)

                        self.measurement_macro(
                            I=I,
                            I_stream=I_stream,
                            Q=Q,
                            Q_stream=Q_stream,
                        )

                    # for_ loop to move the required number of moves in the y direction
                    with for_(j, 0, j < moves_per_edge, j + 1):
                        assign(y, y + movement_direction * y_step_size * 0.25)
                        # save(x, x_st)
                        # save(y, y_st)
                        # if the y coordinate should be 0, ramp to zero to remove fixed point arithmetic errors accumulating
                        with if_(y == 0.0):
                            ramp_to_zero(self.gate2, duration=ramp_to_zero_duration)
                        # playing the constant pulse to move to the next pixel
                        with else_():
                            play(
                                "CW" * amp(movement_direction * y_step_size), self.gate2
                            )

                        # Make sure that we measure after the pulse has settled
                        align(self.gate1, self.gate2, self.measured_element)
                        if (
                            wait_time >= 4
                        ):  # if logic to enable wait_time = 0 without error
                            wait(wait_time, self.measured_element)

                        self.measurement_macro(
                            I=I,
                            I_stream=I_stream,
                            Q=Q,
                            Q_stream=Q_stream,
                        )

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
                    assign(
                        x, x + movement_direction * x_step_size * 0.5
                    )  # updating the x location
                    # save(x, x_st)
                    # save(y, y_st)
                    # if the x coordinate should be 0, ramp to zero to remove fixed point arithmetic errors accumulating
                    with if_(x == 0.0):
                        ramp_to_zero(self.gate1, duration=ramp_to_zero_duration)
                    # playing the constant pulse to move to the next pixel
                    with else_():
                        play("CW" * amp(movement_direction * x_step_size), self.gate1)

                    # Make sure that we measure after the pulse has settled
                    align(self.gate1, self.gate2, self.measured_element)
                    if wait_time >= 4:
                        wait(wait_time, self.measured_element)

                    self.measurement_macro(
                        I=I,
                        I_stream=I_stream,
                        Q=Q,
                        Q_stream=Q_stream,
                    )

                # aligning and ramping to zero to return to initial state
                align(self.gate1, self.gate2, self.measured_element)
                ramp_to_zero(self.gate1, duration=ramp_to_zero_duration)
                ramp_to_zero(self.gate2, duration=ramp_to_zero_duration)
                wait(1000)

            with stream_processing():
                for stream_name, stream in zip(["I", "Q"], [I_stream, Q_stream]):
                    stream.buffer(resolution**2).save(
                        stream_name
                    )  # .buffer(resolution**2)
                x_st.save_all("x")
                y_st.save_all("y")

        return spiral_scan

    def send_input_streams(
        self,
    ):
        self.running_job.insert_input_stream(
            "ranges_input_stream", [self.gate1_range, self.gate2_range]
        )
        self.running_job.insert_input_stream("update_input_stream", [True])
        # self.running_job.insert_input_stream('resolution_input_stream', self.resolution)

    def start_measurement(
        self,
    ):
        self.running_job = self.qm.execute(self.program)
        self.send_input_streams()
        sleep(5)
        self.data_fetcher = fetching_tool(
            self.running_job,
            data_list=[
                "I",
                "Q",
            ],
            mode="live",
        )
        print("REMEMBER TO END MEASUREMENT")

    def fetch_results(
        self,
    ):
        if hasattr(self, "data_fetcher"):
            pass
        else:
            raise Exception(
                'data fetcher not started, run "start_measurement" before trying to fetch results'
            )

        if self.update:
            self.send_input_streams()
            self.update = False
        # elif self.running_job.is_paused(): # not sure this is enough to keep it continously running
        else:
            self.running_job.insert_input_stream("update_input_stream", [False])

        I, Q = self.data_fetcher.fetch_all()
        amplitude = I**2 + Q**2
        self.order = spiral_order(self.resolution)
        return amplitude[self.order]

    def end_measurement(
        self,
    ):
        print(f"program ended: {self.running_job.halt()}")
