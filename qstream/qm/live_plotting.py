import os
import tempfile
import qcodes as qc
from qstream.example_instruments import FilterInstrument
from qstream.livestream import LiveStream
from qcodes import initialise_or_create_database_at, load_or_create_experiment
from qstream.videoinstrument import VideoInstrument
from qstream.qm.live_plotting_buttons import start_stop_extra_step_wrapper
from functools import partial


class Live_plot_handler:
    def __init__(self, opx_controller, resolution, extra_controllers=None):
        self.opx_controller = opx_controller

        # tmp_path = tempfile.gettempdir()
        # source_db_path = os.path.join(tmp_path, "source.db")
        # initialise_or_create_database_at(source_db_path)
        # exp = load_or_create_experiment("for_test", sample_name="no sample")

        self.video = VideoInstrument(
            name="video",
            data_func=self.opx_controller.fetch_results,
            n_points=(resolution, resolution),
        )

        virtual_range = qc.Parameter(
            name="virtual1_range",
            label="virtual1_range",
            set_cmd=self.opx_controller.scan_range,
            get_cmd=self.opx_controller.scan_range,
        )

        # virtual2_range = qc.Parameter(
        #     name="virtual2_range",
        #     label="virtual2_range",
        #     set_cmd=self.opx_controller.set_virtual2_range,
        #     get_cmd=lambda: self.opx_controller.virtual_ranges[1],
        # )

        self.controllers = {
            "scan_range": (virtual_range, 0.1, self.opx_controller.scan_range()),
            # "v_gate2_range": (virtual2_range, 0.1, self.opx_controller.virtual_ranges[1]),
        }
        for virt_setter in self.opx_controller.virtual_setters.keys():
            self.controllers[virt_setter] = (
                qc.Parameter(
                    name=virt_setter,
                    label=virt_setter,
                    set_cmd=self.opx_controller.virtual_setters[virt_setter],
                    get_cmd=self.opx_controller.virtual_getters[virt_setter],
                ),
                0.01,
                self.opx_controller.virtual_getters[virt_setter](),
            )

        if extra_controllers is not None:
            for controller_name, controller_item in extra_controllers.items():
                self.controllers[controller_name] = controller_item

        # self.extra_step_func = partial(
        #     start_stop_extra_step_wrapper, self.opx_controller
        # )

    def start_stream(self, refresh_period=3000):
        self.opx_controller.start_acquisition()
        live = LiveStream(
            video=self.video,
            controllers=self.controllers,
            port=0,
            refresh_period=refresh_period,
            extra_step=self.extra_step_func,
        )
