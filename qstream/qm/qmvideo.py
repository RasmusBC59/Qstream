from qstream.qm.start_stop import StartStop
import os
import tempfile
import qcodes as qc
from qstream.example_instruments import FilterInstrument
from qstream.livestream import LiveStream
from qcodes import initialise_or_create_database_at, load_or_create_experiment
from qstream.videoinstrument import VideoInstrument
from qstream.qm.OPX_live_controller import OPX_live_controller


class QMVideo:
    def __init__(self, resolution, config) -> None:
        self.opx_live_controller = OPX_live_controller()
        self.video = VideoInstrument(
            name="video",
            data_func=self.opx_live_controller.fetch_results,
            n_points=(resolution, resolution),
        )

    def start_streaming(self):
        LiveStream(
            video=self.video, start_stop=StartStop(self.opx_live_controller.running_job)
        )
