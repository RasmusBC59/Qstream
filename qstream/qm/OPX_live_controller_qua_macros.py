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

    print('these voltages are in OPX output voltages')
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
