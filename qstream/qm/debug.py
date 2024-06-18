
# Single QUA script generated at 2023-05-08 10:08:51.929726
# QUA library version: 1.1.1

from qm.qua import *

with program() as prog:
    input_stream_ranges_input_stream = declare_input_stream(fixed, 'ranges_input_stream', size=2)
    input_stream_update_input_stream = declare_input_stream(bool, 'update_input_stream', )
    input_stream_virtualization_input_stream = declare_input_stream(fixed, 'virtualization_input_stream', size=4)
    v1 = declare(fixed, )
    v2 = declare(fixed, )
    v3 = declare(fixed, )
    v4 = declare(fixed, )
    v5 = declare(fixed, )
    v6 = declare(fixed, )
    v7 = declare(int, )
    v8 = declare(int, )
    v9 = declare(int, )
    v10 = declare(fixed, value=0)
    v11 = declare(fixed, value=0)
    v12 = declare(int, )
    v13 = declare(int, )
    v14 = declare(fixed, )
    v15 = declare(fixed, )
    v16 = declare(fixed, )
    with infinite_loop_():
        advance_input_stream(input_stream_update_input_stream)
        with if_(input_stream_update_input_stream):
            advance_input_stream(input_stream_ranges_input_stream)
            advance_input_stream(input_stream_virtualization_input_stream)
            assign(v1, (input_stream_ranges_input_stream[0]*0.016666666666666666))
            assign(v2, (input_stream_ranges_input_stream[1]*0.016666666666666666))
            assign(v3, (input_stream_virtualization_input_stream[0]*v1))
            assign(v4, (input_stream_virtualization_input_stream[1]*v1))
            assign(v5, (input_stream_virtualization_input_stream[2]*v2))
            assign(v6, (input_stream_virtualization_input_stream[3]*v2))
        with for_(v9,0,(v9<0),(v9+1)):
            assign(v12, 1)
            assign(v13, 0)
            assign(v14, 1)
            assign(v10, 0)
            r1 = declare_stream()
            save(v10, r1)
            assign(v11, 0)
            r2 = declare_stream()
            save(v11, r2)
            measure("readout_pulse_5us", "bottom_left_DQD_readout", None, demod.full("cos", v15, ""), demod.full("sin", v16, ""))
            r3 = declare_stream()
            save(v15, r3)
            r4 = declare_stream()
            save(v16, r4)
            with while_((v13<3660)):
                with for_(v7,0,(v7<v12),(v7+1)):
                    play("CW"*amp((v14*v3)), "gate_46", duration=1235)
                    assign(v10, (v10+(v14*v3)))
                    save(v10, r1)
                    play("CW"*amp((v14*v4)), "gate_41", duration=1235)
                    assign(v11, (v11+(v14*v4)))
                    save(v11, r2)
                    measure("readout_pulse_5us", "bottom_left_DQD_readout", None, demod.full("cos", v15, ""), demod.full("sin", v16, ""))
                    save(v15, r3)
                    save(v16, r4)
                with for_(v8,0,(v8<v12),(v8+1)):
                    play("CW"*amp((v14*v5)), "gate_46", duration=1235)
                    assign(v10, (v10+(v14*v5)))
                    save(v10, r1)
                    play("CW"*amp((v14*v6)), "gate_41", duration=1235)
                    assign(v11, (v11+(v14*v6)))
                    save(v11, r2)
                    measure("readout_pulse_5us", "bottom_left_DQD_readout", None, demod.full("cos", v15, ""), demod.full("sin", v16, ""))
                    save(v15, r3)
                    save(v16, r4)
                assign(v13, (v13+(2*v12)))
                assign(v14, (v14*-1))
                assign(v12, (v12+1))
            with for_(v7,0,(v7<(v12-1)),(v7+1)):
                play("CW"*amp((v14*v3)), "gate_46", duration=1235)
                assign(v10, (v10+(v14*v3)))
                save(v10, r1)
                play("CW"*amp((v14*v4)), "gate_41", duration=1235)
                assign(v11, (v11+(v14*v4)))
                save(v11, r2)
                measure("readout_pulse_5us", "bottom_left_DQD_readout", None, demod.full("cos", v15, ""), demod.full("sin", v16, ""))
                save(v15, r3)
                save(v16, r4)
            ramp_to_zero("gate_46", 1)
            ramp_to_zero("gate_41", 1)
            wait(1000, )
    with stream_processing():
        r3.buffer(3721).save("I")
        r4.buffer(3721).save("Q")
        r1.buffer(3721).save_all("gate_46")
        r2.buffer(3721).save_all("gate_41")


config = {
    "version": 1,
    "controllers": {
        "con1": {
            "analog_outputs": {
                "1": {
                    "offset": 0,
                },
                "4": {
                    "offset": -0.0072,
                },
                "5": {
                    "offset": -0.0072,
                },
            },
            "digital_outputs": {
                "2": {},
            },
            "analog_inputs": {
                "2": {
                    "offset": 0,
                },
            },
        },
    },
    "elements": {
        "gate_46": {
            "singleInput": {
                "port": [con1, 4],
            },
            "intermediate_frequency": 0.0,
            "hold_offset": {
                "duration": 24,
            },
            "operations": {
                "CW": "CW",
            },
        },
        "gate_41": {
            "singleInput": {
                "port": [con1, 5],
            },
            "intermediate_frequency": 0.0,
            "hold_offset": {
                "duration": 24,
            },
            "operations": {
                "CW": "CW",
            },
        },
        "bottom_left_DQD_readout": {
            "singleInput": {
                "port": [con1, 1],
            },
            "intermediate_frequency": 180555556,
            "operations": {
                "readout_pulse_100us": "readout_pulse_100us",
                "readout_pulse_10us": "readout_pulse_10us",
                "readout_pulse_5us": "readout_pulse_5us",
                "readout_pulse_3ms": "readout_pulse_3ms",
                "readout_pulse_20ms": "readout_pulse_20ms",
                "readout_pulse_3us": "readout_pulse_3us",
                "readout_pulse_50us": "readout_pulse_50us",
                "readout_pulse_t2star": "readout_pulse_t2star",
                "readout_pulse_t2star_full_demod": "readout_pulse_t2star_full_demod",
            },
            "outputs": {
                "out1": [con1, 2],
            },
            "time_of_flight": 500,
            "smearing": 0,
        },
    },
    "pulses": {
        "CW": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "single": "const_wf",
            },
        },
        "readout_pulse_100us": {
            "operation": "measurement",
            "length": 99560,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_100us",
                "sin": "sin_100us",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_10us": {
            "operation": "measurement",
            "length": 10000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos",
                "sin": "sin",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_5us": {
            "operation": "measurement",
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_5us",
                "sin": "sin_5us",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_3us": {
            "operation": "measurement",
            "length": 3000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_3us",
                "sin": "sin_3us",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_50us": {
            "operation": "measurement",
            "length": 100000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_50",
                "sin": "sin_50",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_3ms": {
            "operation": "measurement",
            "length": 3000000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_buffered",
                "sin": "sin_buffered",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_20ms": {
            "operation": "measurement",
            "length": 20000000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_buffered",
                "sin": "sin_buffered",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_t2star": {
            "operation": "measurement",
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_t2star",
                "sin": "sin_t2star",
            },
            "digital_marker": "ON",
        },
        "readout_pulse_t2star_full_demod": {
            "operation": "measurement",
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "integration_weights": {
                "cos": "cos_t2star_full_demod",
                "sin": "sin_t2star_full_demod",
            },
            "digital_marker": "ON",
        },
    },
    "waveforms": {
        "const_wf": {
            "type": "constant",
            "sample": 0.25,
        },
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "readout_wf_0_2": {
            "type": "constant",
            "sample": 0.2,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [[1, 0]],
        },
    },
    "integration_weights": {
        "cos_100us": {
            "cosine": [[1.0, 99560]],
            "sine": [[0.0, 99560]],
        },
        "sin_100us": {
            "cosine": [[0.0, 99560]],
            "sine": [[1.0, 99560]],
        },
        "cos": {
            "cosine": [[1.0, 10000]],
            "sine": [[0.0, 10000]],
        },
        "sin": {
            "cosine": [[0.0, 10000]],
            "sine": [[1.0, 10000]],
        },
        "cos_50": {
            "cosine": [[1.0, 100000]],
            "sine": [[0.0, 100000]],
        },
        "sin_50": {
            "cosine": [[0.0, 100000]],
            "sine": [[1.0, 100000]],
        },
        "cos_3us": {
            "cosine": [[1.0, 3000]],
            "sine": [[0.0, 3000]],
        },
        "sin_3us": {
            "cosine": [[0.0, 3000]],
            "sine": [[1.0, 3000]],
        },
        "cos_5us": {
            "cosine": [[1.0, 4940]],
            "sine": [[0.0, 4940]],
        },
        "sin_5us": {
            "cosine": [[0.0, 4940]],
            "sine": [[1.0, 4940]],
        },
        "cos_buffered": {
            "cosine": [[0.001, 3000000]],
            "sine": [[0.0, 3000000]],
        },
        "sin_buffered": {
            "cosine": [[0.0, 3000000]],
            "sine": [[0.001, 3000000]],
        },
        "cos_t2star": {
            "cosine": [[1.0, 4940]],
            "sine": [[0.0, 4940]],
        },
        "sin_t2star": {
            "cosine": [[0.0, 4940]],
            "sine": [[1.0, 4940]],
        },
        "cos_t2star_full_demod": {
            "cosine": [[0.005050505050505051, 4940]],
            "sine": [[0.0, 4940]],
        },
        "sin_t2star_full_demod": {
            "cosine": [[0.0, 4940]],
            "sine": [[0.005050505050505051, 4940]],
        },
    },
}

loaded_config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                },
                "4": {
                    "offset": -0.0072,
                    "delay": 0,
                    "shareable": False,
                },
                "5": {
                    "offset": -0.0072,
                    "delay": 0,
                    "shareable": False,
                },
            },
            "analog_inputs": {
                "2": {
                    "offset": 0.0,
                    "gain_db": 0,
                    "shareable": False,
                },
            },
            "digital_outputs": {
                "2": {
                    "shareable": False,
                },
            },
        },
    },
    "oscillators": {},
    "elements": {
        "gate_46": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "intermediate_frequency": 0.0,
            "operations": {
                "CW": "CW",
            },
            "singleInput": {
                "port": ('con1', 4),
            },
            "hold_offset": {
                "duration": 24,
            },
        },
        "gate_41": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "intermediate_frequency": 0.0,
            "operations": {
                "CW": "CW",
            },
            "singleInput": {
                "port": ('con1', 5),
            },
            "hold_offset": {
                "duration": 24,
            },
        },
        "bottom_left_DQD_readout": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 2),
            },
            "time_of_flight": 500,
            "smearing": 0,
            "intermediate_frequency": 180555556.0,
            "operations": {
                "readout_pulse_100us": "readout_pulse_100us",
                "readout_pulse_10us": "readout_pulse_10us",
                "readout_pulse_5us": "readout_pulse_5us",
                "readout_pulse_3ms": "readout_pulse_3ms",
                "readout_pulse_20ms": "readout_pulse_20ms",
                "readout_pulse_3us": "readout_pulse_3us",
                "readout_pulse_50us": "readout_pulse_50us",
                "readout_pulse_t2star": "readout_pulse_t2star",
                "readout_pulse_t2star_full_demod": "readout_pulse_t2star_full_demod",
            },
            "singleInput": {
                "port": ('con1', 1),
            },
        },
    },
    "pulses": {
        "CW": {
            "length": 100,
            "waveforms": {
                "single": "const_wf",
            },
            "operation": "control",
        },
        "readout_pulse_100us": {
            "length": 99560,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_100us",
                "sin": "sin_100us",
            },
            "operation": "measurement",
        },
        "readout_pulse_10us": {
            "length": 10000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos",
                "sin": "sin",
            },
            "operation": "measurement",
        },
        "readout_pulse_5us": {
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_5us",
                "sin": "sin_5us",
            },
            "operation": "measurement",
        },
        "readout_pulse_3us": {
            "length": 3000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_3us",
                "sin": "sin_3us",
            },
            "operation": "measurement",
        },
        "readout_pulse_50us": {
            "length": 100000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_50",
                "sin": "sin_50",
            },
            "operation": "measurement",
        },
        "readout_pulse_3ms": {
            "length": 3000000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_buffered",
                "sin": "sin_buffered",
            },
            "operation": "measurement",
        },
        "readout_pulse_20ms": {
            "length": 20000000,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_buffered",
                "sin": "sin_buffered",
            },
            "operation": "measurement",
        },
        "readout_pulse_t2star": {
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_t2star",
                "sin": "sin_t2star",
            },
            "operation": "measurement",
        },
        "readout_pulse_t2star_full_demod": {
            "length": 4940,
            "waveforms": {
                "single": "readout_wf_0_2",
            },
            "digital_marker": "ON",
            "integration_weights": {
                "cos": "cos_t2star_full_demod",
                "sin": "sin_t2star_full_demod",
            },
            "operation": "measurement",
        },
    },
    "waveforms": {
        "const_wf": {
            "sample": 0.25,
            "type": "constant",
        },
        "zero_wf": {
            "sample": 0.0,
            "type": "constant",
        },
        "readout_wf_0_2": {
            "sample": 0.2,
            "type": "constant",
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "cos_100us": {
            "cosine": [(1.0, 99560)],
            "sine": [(0.0, 99560)],
        },
        "sin_100us": {
            "cosine": [(0.0, 99560)],
            "sine": [(1.0, 99560)],
        },
        "cos": {
            "cosine": [(1.0, 10000)],
            "sine": [(0.0, 10000)],
        },
        "sin": {
            "cosine": [(0.0, 10000)],
            "sine": [(1.0, 10000)],
        },
        "cos_50": {
            "cosine": [(1.0, 100000)],
            "sine": [(0.0, 100000)],
        },
        "sin_50": {
            "cosine": [(0.0, 100000)],
            "sine": [(1.0, 100000)],
        },
        "cos_3us": {
            "cosine": [(1.0, 3000)],
            "sine": [(0.0, 3000)],
        },
        "sin_3us": {
            "cosine": [(0.0, 3000)],
            "sine": [(1.0, 3000)],
        },
        "cos_5us": {
            "cosine": [(1.0, 4940)],
            "sine": [(0.0, 4940)],
        },
        "sin_5us": {
            "cosine": [(0.0, 4940)],
            "sine": [(1.0, 4940)],
        },
        "cos_buffered": {
            "cosine": [(0.001, 3000000)],
            "sine": [(0.0, 3000000)],
        },
        "sin_buffered": {
            "cosine": [(0.0, 3000000)],
            "sine": [(0.001, 3000000)],
        },
        "cos_t2star": {
            "cosine": [(1.0, 4940)],
            "sine": [(0.0, 4940)],
        },
        "sin_t2star": {
            "cosine": [(0.0, 4940)],
            "sine": [(1.0, 4940)],
        },
        "cos_t2star_full_demod": {
            "cosine": [(0.005050505050505051, 4940)],
            "sine": [(0.0, 4940)],
        },
        "sin_t2star_full_demod": {
            "cosine": [(0.0, 4940)],
            "sine": [(0.005050505050505051, 4940)],
        },
    },
    "mixers": {},
}


