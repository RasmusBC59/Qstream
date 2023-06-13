import os
import tempfile
import qcodes as qc
from qstream.example_instruments import FilterInstrument
from qstream.livestream import LiveStream
from qcodes import initialise_or_create_database_at, load_or_create_experiment
from qstream.videoinstrument import VideoInstrument


class Live_plot_handler:
    def __init__(self, opx_controller, resolution):
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

        virtual1_range = qc.Parameter(
            name="virtual1_range",
            label="virtual1_range",
            set_cmd=self.opx_controller.set_virtual1_range,
            get_cmd=lambda: self.opx_controller.virtual_ranges[0],
        )

        virtual2_range = qc.Parameter(
            name="virtual2_range",
            label="virtual2_range",
            set_cmd=self.opx_controller.set_virtual2_range,
            get_cmd=lambda: self.opx_controller.virtual_ranges[1],
        )

        self.controllers = {
            # "BNC41": (qdac_2.BNC41, 0.01, qdac_2.BNC41()), # -0.05
            # "BNC46": (qdac_2.BNC46, 0.01, qdac_2.BNC46()), # -0.16
            "gate1_range": (virtual1_range, 0.1, self.opx_controller.virtual_ranges[0]),
            "gate2_range": (virtual2_range, 0.1, self.opx_controller.virtual_ranges[1]),
        }
        for virt_setter in self.opx_controller.virtual_setters.keys():
            self.controllers[virt_setter] = (
                qc.Parameter(
                    name=virt_setter,
                    label=virt_setter,
                    set_cmd=self.opx_controller.virtual_setters[virt_setter],
                    get_cmd=self.opx_controller.virtual_getters[virt_setter],
                ),
                0.2,
                self.opx_controller.virtual_getters[virt_setter](),
            )

    def start_stream(self, refresh_period=3000):
        self.opx_controller.start_measurement()
        live = LiveStream(
            video=self.video,
            controllers=self.controllers,
            port=0,
            refresh_period=refresh_period,
        )
