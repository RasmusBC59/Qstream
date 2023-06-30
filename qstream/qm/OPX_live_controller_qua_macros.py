from qm.qua import (
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
    ramp,
    save,
    fixed,
    demod,
    declare_input_stream,
    advance_input_stream,
    amp,
    if_,
    ramp_to_zero,
    while_,
    assign,
    infinite_loop_,
    FUNCTIONS,
    pause,
)

import numpy as np


def angle_step_macro_maker(
    angle_degree, det_amp, duration_clk_cycles, elements, dividers, jump_amp, jump_pulse
):
    det_min = {
        elements[0]: det_amp
        * np.cos(angle_degree * np.pi / 180)
        * dividers[elements[0]]
        / jump_amp,
        elements[1]: det_amp
        * np.sin(angle_degree * np.pi / 180)
        * dividers[elements[1]]
        / jump_amp,
    }

    print("these values are in device voltages")
    print(f"{elements[0]} step: {det_min[elements[0]]/dividers[elements[0]]*jump_amp}V")
    print(f"{elements[1]} step: {det_min[elements[1]]/dividers[elements[1]]*jump_amp}V")

    print("these voltages are in OPX output voltages")
    print(f"{elements[0]} step: {det_min[elements[0]]}V")
    print(f"{elements[1]} step: {det_min[elements[1]]}V")

    def angle_step_macro():
        play(
            jump_pulse * amp(det_min[elements[0]]),
            elements[0],
            duration=duration_clk_cycles,
        )
        play(
            jump_pulse * amp(det_min[elements[1]]),
            elements[1],
            duration=duration_clk_cycles,
        )

        play(jump_pulse * amp(-det_min[elements[0]]), elements[0], duration=4)
        play(jump_pulse * amp(-det_min[elements[1]]), elements[1], duration=4)

    def inverse_angle_step_macro():
        play(
            jump_pulse * amp(-det_min[elements[0]]),
            elements[0],
            duration=duration_clk_cycles,
        )
        play(
            jump_pulse * amp(-det_min[elements[1]]),
            elements[1],
            duration=duration_clk_cycles,
        )

        play(jump_pulse * amp(det_min[elements[0]]), elements[0], duration=4)
        play(jump_pulse * amp(det_min[elements[1]]), elements[1], duration=4)

    return angle_step_macro, inverse_angle_step_macro


def PSB_tringle(
    M_point_V,
    E_point_V,
    S_point_V,
    ramp_time_ns,
    gate_1,
    gate_2,
    jump_pulse="CW",
    jump_pulse_amp=0.25,
    dividers=np.array([1, 1]),
):
    # M_point_V = np.array([0, 0])
    M_point_V = M_point_V * dividers
    E_point_V = E_point_V * dividers
    S_point_V = S_point_V * dividers

    M_to_E_jump = E_point_V - M_point_V
    E_to_S_jump = S_point_V - E_point_V
    S_to_M_jump = (M_point_V - S_point_V).tolist()

    M_to_E_ramp_rate = (M_to_E_jump / ramp_time_ns).tolist()
    E_to_S_ramp_rate = (E_to_S_jump / ramp_time_ns).tolist()

    ramp_time_clk_cycles = ramp_time_ns // 4

    def triangle_macro():
        play(ramp(M_to_E_ramp_rate[0]), gate_1, ramp_time_clk_cycles)
        play(ramp(M_to_E_ramp_rate[1]), gate_2, ramp_time_clk_cycles)

        play(ramp(E_to_S_ramp_rate[0]), gate_1, ramp_time_clk_cycles)
        play(ramp(E_to_S_ramp_rate[1]), gate_2, ramp_time_clk_cycles)

        play(jump_pulse * amp(S_to_M_jump[0] / jump_pulse_amp), gate_1, 4)
        play(jump_pulse * amp(S_to_M_jump[1] / jump_pulse_amp), gate_2, 4)

    def inverse_triangle_macro():
        play(ramp(-M_to_E_ramp_rate[0]), gate_1, ramp_time_clk_cycles)
        play(ramp(-M_to_E_ramp_rate[1]), gate_2, ramp_time_clk_cycles)

        play(ramp(-E_to_S_ramp_rate[0]), gate_1, ramp_time_clk_cycles)
        play(ramp(-E_to_S_ramp_rate[1]), gate_2, ramp_time_clk_cycles)

        play(jump_pulse * amp(-S_to_M_jump[0] / jump_pulse_amp), gate_1, 4)
        play(jump_pulse * amp(-S_to_M_jump[1] / jump_pulse_amp), gate_2, 4)

    return triangle_macro, inverse_triangle_macro
