import os
import tempfile
from qstream.example_instruments import FilterInstrument
from qstream.livestream import LiveStream
from qcodes import initialise_or_create_database_at, load_or_create_experiment
from qstream.videoinstrument import VideoInstrument

tmp_path = tempfile.gettempdir()
source_db_path = os.path.join(tmp_path, "source.db")
initialise_or_create_database_at(source_db_path)
exp = load_or_create_experiment("for_test", sample_name="no sample")
test_instrument = FilterInstrument("test_instrument")
video = VideoInstrument(
    name="video",
    data_func=test_instrument.spectrum_and_noise.get,
    n_points=(40, 2208),
)


controllers = {
    "phase_x": (test_instrument.phase_x, 0.1, 0),
    "phase_y": (test_instrument.phase_y, 0.1, 0),
}

live = LiveStream(video=video, controllers=controllers, port=0, refresh_period=500)
