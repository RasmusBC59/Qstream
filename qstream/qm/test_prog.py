
# Single QUA script generated at 2024-06-17 10:25:49.297466
# QUA library version: 1.1.4

from qm.qua import *

with program() as prog:
    v1 = declare(fixed, )
    v2 = declare(int, )
    v3 = declare(fixed, )
    v4 = declare(fixed, )
    v5 = declare(fixed, )
    v6 = declare(fixed, )
    with infinite_loop_():
        with for_(v1,-1.0,(v1<1.02),(v1+0.040000000000000036)):
            align("left_inner_dot_plunger", "right_inner_dot_plunger")
            align("T_sensor")
            play("slow_pulse"*amp(v1), "left_inner_dot_plunger")
            play("slow_pulse"*amp(v1), "right_inner_dot_plunger")
            play("big_pulse", "left_inner_dot_plunger")
            play("big_pulse", "right_inner_dot_plunger")
            with for_(v2,0,(v2<=50),(v2+1)):
                play("small_pulse", "left_inner_dot_plunger")
                play("small_pulse", "right_inner_dot_plunger")
                wait(25, )
                measure("readout", "T_sensor", None, demod.full("iw1", v3, "out1"), demod.full("iw2", v4, "out1"))
                r1 = declare_stream()
                save(v3, r1)
                r2 = declare_stream()
                save(v4, r2)
            ramp_to_zero("left_inner_dot_plunger", 1)
            ramp_to_zero("right_inner_dot_plunger", 1)
            play("slow_pulse"*amp((-1*v1)), "left_inner_dot_plunger")
            play("slow_pulse"*amp((-1*v1)), "right_inner_dot_plunger")
            play("big_pulse"*amp(-1), "left_inner_dot_plunger")
            play("big_pulse"*amp(-1), "right_inner_dot_plunger")
            with for_(v2,0,(v2<=50),(v2+1)):
                play("small_pulse"*amp(-1), "left_inner_dot_plunger")
                play("small_pulse"*amp(-1), "right_inner_dot_plunger")
                wait(25, )
                measure("readout", "T_sensor", None, demod.full("iw1", v5, "out1"), demod.full("iw2", v6, "out1"))
            ramp_to_zero("left_inner_dot_plunger", 1)
            ramp_to_zero("right_inner_dot_plunger", 1)
    with stream_processing():
        r1.buffer(30, 2601).map(FUNCTIONS.average(0)).save("I")
        r2.buffer(30, 2601).map(FUNCTIONS.average(0)).save("Q")


config = {
    "version": 1,
    "controllers": {
        "con1": {
            "analog_outputs": {
                "4": {
                    "offset": 0.0,
                },
                "6": {
                    "offset": 0.0,
                },
                "1": {
                    "offset": 0.0,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.0,
                },
            },
        },
    },
    "elements": {
        "left_inner_dot_plunger": {
            "operations": {
                "slow_pulse": "left_inner_dot_plunger.slow_pulse.pulse",
                "big_pulse": "left_inner_dot_plunger.big_pulse.pulse",
                "small_pulse": "left_inner_dot_plunger.small_pulse.pulse",
            },
            "singleInput": {
                "port": ('con1', 4),
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 200,
            },
        },
        "right_inner_dot_plunger": {
            "operations": {
                "slow_pulse": "right_inner_dot_plunger.slow_pulse.pulse",
                "big_pulse": "right_inner_dot_plunger.big_pulse.pulse",
                "small_pulse": "right_inner_dot_plunger.small_pulse.pulse",
            },
            "singleInput": {
                "port": ('con1', 6),
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 200,
            },
        },
        "T_sensor": {
            "operations": {
                "readout": "T_sensor.readout.pulse",
            },
            "singleInput": {
                "port": ('con1', 1),
            },
            "intermediate_frequency": 176553106,
            "outputs": {
                "out1": ('con1', 1),
            },
            "smearing": 0,
            "time_of_flight": 400,
        },
    },
    "pulses": {
        "const_pulse": {
            "operation": "control",
            "length": 1000,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
        },
        "T_sensor.readout.pulse": {
            "operation": "measurement",
            "length": 1000,
            "digital_marker": "ON",
            "waveforms": {
                "single": "T_sensor.readout.wf",
            },
            "integration_weights": {
                "iw1": "T_sensor.readout.iw1",
                "iw2": "T_sensor.readout.iw2",
                "iw3": "T_sensor.readout.iw3",
            },
        },
        "left_inner_dot_plunger.slow_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.slow_pulse.wf",
            },
        },
        "right_inner_dot_plunger.slow_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.slow_pulse.wf",
            },
        },
        "left_inner_dot_plunger.big_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.big_pulse.wf",
            },
        },
        "right_inner_dot_plunger.big_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.big_pulse.wf",
            },
        },
        "left_inner_dot_plunger.small_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.small_pulse.wf",
            },
        },
        "right_inner_dot_plunger.small_pulse.pulse": {
            "operation": "control",
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.small_pulse.wf",
            },
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.1,
        },
        "T_sensor.readout.wf": {
            "type": "constant",
            "sample": 0.1,
        },
        "left_inner_dot_plunger.slow_pulse.wf": {
            "type": "constant",
            "sample": 0.4305,
        },
        "right_inner_dot_plunger.slow_pulse.wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "left_inner_dot_plunger.big_pulse.wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "right_inner_dot_plunger.big_pulse.wf": {
            "type": "constant",
            "sample": 0.5,
        },
        "left_inner_dot_plunger.small_pulse.wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "right_inner_dot_plunger.small_pulse.wf": {
            "type": "constant",
            "sample": 0.02,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [[1, 0]],
        },
    },
    "integration_weights": {
        "T_sensor.readout.iw1": {
            "cosine": [(1.0, 1000)],
            "sine": [(-0.0, 1000)],
        },
        "T_sensor.readout.iw2": {
            "cosine": [(0.0, 1000)],
            "sine": [(1.0, 1000)],
        },
        "T_sensor.readout.iw3": {
            "cosine": [(-0.0, 1000)],
            "sine": [(-1.0, 1000)],
        },
    },
    "mixers": {},
    "oscillators": {},
}

loaded_config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "4": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                },
                "6": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                },
                "1": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.0,
                    "gain_db": 0,
                    "shareable": False,
                },
            },
        },
    },
    "oscillators": {},
    "elements": {
        "left_inner_dot_plunger": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "operations": {
                "slow_pulse": "left_inner_dot_plunger.slow_pulse.pulse",
                "big_pulse": "left_inner_dot_plunger.big_pulse.pulse",
                "small_pulse": "left_inner_dot_plunger.small_pulse.pulse",
            },
            "singleInput": {
                "port": ('con1', 4),
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 200,
            },
        },
        "right_inner_dot_plunger": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "operations": {
                "slow_pulse": "right_inner_dot_plunger.slow_pulse.pulse",
                "big_pulse": "right_inner_dot_plunger.big_pulse.pulse",
                "small_pulse": "right_inner_dot_plunger.small_pulse.pulse",
            },
            "singleInput": {
                "port": ('con1', 6),
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 200,
            },
        },
        "T_sensor": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1),
            },
            "time_of_flight": 400,
            "smearing": 0,
            "intermediate_frequency": 176553106.0,
            "operations": {
                "readout": "T_sensor.readout.pulse",
            },
            "singleInput": {
                "port": ('con1', 1),
            },
        },
    },
    "pulses": {
        "const_pulse": {
            "length": 1000,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "operation": "control",
        },
        "T_sensor.readout.pulse": {
            "length": 1000,
            "waveforms": {
                "single": "T_sensor.readout.wf",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "iw1": "T_sensor.readout.iw1",
                "iw2": "T_sensor.readout.iw2",
                "iw3": "T_sensor.readout.iw3",
            },
            "operation": "measurement",
        },
        "left_inner_dot_plunger.slow_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.slow_pulse.wf",
            },
            "operation": "control",
        },
        "right_inner_dot_plunger.slow_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.slow_pulse.wf",
            },
            "operation": "control",
        },
        "left_inner_dot_plunger.big_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.big_pulse.wf",
            },
            "operation": "control",
        },
        "right_inner_dot_plunger.big_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.big_pulse.wf",
            },
            "operation": "control",
        },
        "left_inner_dot_plunger.small_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "left_inner_dot_plunger.small_pulse.wf",
            },
            "operation": "control",
        },
        "right_inner_dot_plunger.small_pulse.pulse": {
            "length": 1200,
            "waveforms": {
                "single": "right_inner_dot_plunger.small_pulse.wf",
            },
            "operation": "control",
        },
    },
    "waveforms": {
        "zero_wf": {
            "sample": 0.0,
            "type": "constant",
        },
        "const_wf": {
            "sample": 0.1,
            "type": "constant",
        },
        "T_sensor.readout.wf": {
            "sample": 0.1,
            "type": "constant",
        },
        "left_inner_dot_plunger.slow_pulse.wf": {
            "sample": 0.4305,
            "type": "constant",
        },
        "right_inner_dot_plunger.slow_pulse.wf": {
            "sample": 0.0,
            "type": "constant",
        },
        "left_inner_dot_plunger.big_pulse.wf": {
            "sample": 0.0,
            "type": "constant",
        },
        "right_inner_dot_plunger.big_pulse.wf": {
            "sample": 0.5,
            "type": "constant",
        },
        "left_inner_dot_plunger.small_pulse.wf": {
            "sample": 0.0,
            "type": "constant",
        },
        "right_inner_dot_plunger.small_pulse.wf": {
            "sample": 0.02,
            "type": "constant",
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "T_sensor.readout.iw1": {
            "cosine": [(1.0, 1000)],
            "sine": [(0.0, 1000)],
        },
        "T_sensor.readout.iw2": {
            "cosine": [(0.0, 1000)],
            "sine": [(1.0, 1000)],
        },
        "T_sensor.readout.iw3": {
            "cosine": [(0.0, 1000)],
            "sine": [(-1.0, 1000)],
        },
    },
    "mixers": {},
}


