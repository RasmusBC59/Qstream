from panel.widgets import Button


class StartStop:
    def __init__(self, job) -> None:
        self.job = job
        self.run_button = Button(name="Run", button_type="default")
        self.run_button.on_click(self.run_event)
        self.set_button_color()

    def run_event(self, event):
        self.start_stop_sweep()

    def start_stop_sweep(self):
        if self.state:
            self.job.halt()
            self.set_button_color()
        else:
            self.job.resume()

    @property
    def state(self):
        return self.job.is_paused()

    def set_button_color(self):
        if self.state:
            self.run_button.button_type = "success"
        else:
            self.run_button.button_type = "danger"
