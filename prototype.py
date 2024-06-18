# %%
import os
import tempfile
from qstream.example_instruments import FilterInstrument
from qstream.livestream import LiveStream
from qcodes import initialise_or_create_database_at, load_or_create_experiment
from qstream.videoinstrument import VideoInstrument
from panel.widgets import Button
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

video.x.V_dc(0.2)
video.x.V_start(-0.5)
video.x.V_stop(0.5)
video.x.V_axis.reset()

video.y.V_dc(-0.2)
video.y.V_start(-0.5)
video.y.V_stop(0.5)
video.y.V_axis.reset()

controllers = {
    "phase_x": (test_instrument.phase_x, 0.1, 0),
    "phase_y": (test_instrument.phase_y, 0.1, 0),
}

class StartStop():
    def __init__(self) -> None:
        self.state = False    
        self.run_button = Button(name='Run', button_type='default')
        self.run_button.on_click(self.run_event)

    def run_event(self, event):
        self.start_stop_sweep()


    def start_stop_sweep(self):
        if self.state:
            self.state = False
            self.run_button.button_type = 'danger'
        else:
            self.state = True
            self.run_button.button_type = 'success'
# %%
live = LiveStream(video=video, controllers=controllers, port=0, refresh_period=100, start_stop=StartStop())

# %%
live = LiveStream(video=video, controllers=controllers, port=0, refresh_period=100)
# %%
import numpy as np 
A = np.array([[6, 1, 1],
              [4, -2, 5],
              [2, 8, 7]])
# %%
B = np.linalg.inv(A)
# %%
print(B)
# %%
B.dot([1,0,0])
