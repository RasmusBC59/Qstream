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


class Stop_job:
    def __init__(self, job) -> None:
        self.job = job
        self.run_button = Button(name="Run", button_type="default")
        self.run_button.on_click(self.stop_job)

    def stop_job(
        self,
    ):
        self.job.halt()


class Start_stop_extra_step:
    def __init__(self, start_stop_extra_step, reset_average) -> None:
        self.start_stop_extra_step = start_stop_extra_step
        self.reset_average = reset_average
        self.button = Button(name="start/stop extra step", button_type="default")
        self.button.on_click(self.run_event)

    def run_event(self, event):
        self.start_stop_extra_step()
        self.reset_average(event)


def start_stop_extra_step_wrapper(OPX_live_controller):
    OPX_live_controller.perform_extra_step = not OPX_live_controller.perform_extra_step
