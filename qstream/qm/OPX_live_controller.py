from functools import partial
from qualang_tools.results import fetching_tool
from qm.qua import (program,
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
                    infinite_loop_)

import numpy as np
from time import sleep

def spiral_order(N: int):
    # casting to int if necessary
    if not isinstance(N, int):
        N = int(N)
    # asserting that N is odd
    N = N if N % 2 == 1 else N + 1

    # setting i, j to be in the middle of the image
    i, j = (N - 1) // 2, (N - 1) // 2

    # creating array to hold the ordering
    order = np.zeros(shape=(N, N), dtype=int)

    sign = +1  # the direction which to move along the respective axis
    number_of_moves = 1  # the number of moves needed for the current edge
    total_moves = 0  # the total number of moves completed so far

    # spiralling outwards along x edge then y
    while total_moves < N**2 - N:
        for _ in range(number_of_moves):
            i = i + sign  # move one step in left (sign = -1) or right (sign = +1)
            total_moves = total_moves + 1
            order[i, j] = total_moves  # updating the ordering array

        for _ in range(number_of_moves):
            j = j + sign  # move one step in down (sign = -1) or up (sign = +1)
            total_moves = total_moves + 1
            order[i, j] = total_moves
        sign = sign * -1  # the next moves will be in the opposite direction
        number_of_moves = number_of_moves + 1  # the next edges will require one more step

    # filling the final x edge, which cannot cleanly be done in the above while loop
    for _ in range(number_of_moves - 1):
        i = i + sign  # move one step in left (sign = -1) or right (sign = +1)
        total_moves = total_moves + 1
        order[i, j] = total_moves

    return order

class OPX_live_controller():
    """
    Modified from: https://github.com/qua-platform/qua-libs/tree/main/Quantum-Control-Applications/Quantum-Dots/Use%20Case%201%20-%20Fast%202D%20Scans
    """
    def __init__(self,
                 elements,
                 virtual_ranges,
                 resolution,
                 qm,
                 readout_pulse,
                 config,
                 virtualization_matrix = None,
                 wait_time = 0,
                 jump_pulse = 'CW', 
                 measured_element = 'bottom_left_DQD_readout',
                 dividers = {'gate_41': 7.9, 'gate_46': 8.1}, 
                 perform_measurement = True,
                 run_test = False
                 ):
        
        assert len(dividers) == len(elements), f'Each element must have an associated divider, {len(elements)} elements were given with {len(dividers)}'
        assert elements == list(dividers.keys()), f'elements and dividers must be given in same order, could be fixed later.'
        
        self.qm = qm

        if (np.array(virtual_ranges) > 0.5).any():
            raise Exception(f'Virtual ranges must be given in units of Volt, values above 0.5 will raise this error, values given were:{virtual_ranges}')
        
        # get length of readout pulse, likely not need as time will be set by measurement anyway (possibly only with aligns)
        self.readout_pulse_length = config['pulses'][readout_pulse]['length']//4 #length in clockcycles
        self.readout_pulse = readout_pulse

        # get jump pulse and jump pulse amplitude, will be used to output correct voltages
        self.jump_pulse = jump_pulse
        CW_pulse = config['pulses'][jump_pulse]['waveforms']['single']
        self.jump_amp = config['waveforms'][CW_pulse]['sample']

        self.measured_element = measured_element
        self.elements = elements
        self.virtual_ranges = virtual_ranges

        if virtualization_matrix is None:
            self.virtualization_matrix = np.eye(2, len(elements))
        else:
            self.virtualization_matrix = virtualization_matrix
            assert virtualization_matrix.shape == (2,len(elements)), f'wrong shape of virtualization matrix, expected {(2,len(elements))} got {virtualization_matrix.shape}'
        
        self.dividers = dividers
        self.apply_dividers()
        self.wait_time = wait_time
        
        

        self.set_resolution(resolution)
        self.set_virtual1_range(virtual_ranges[0])
        self.set_virtual2_range(virtual_ranges[1])

        self.update = True
        self.perform_measurement = perform_measurement # only for testing
        self.run_test = run_test # only for testing

        self.program = self.make_program()

        self.virtual_setters = self.make_virt_setters(['virtual1', 'virtual2'], elements)
        self.virtual_getters = self.make_virt_getters(['virtual1', 'virtual2'], elements)
    
    def set_virt_element(self, value, virtual_index, element):
        self.virtualization_matrix[virtual_index, element] = value
        self.apply_dividers()
        self.update = True
    
    def get_virt_element(self, virtual_index, element):
        return self.virtualization_matrix[virtual_index, element]
    
    def apply_dividers(self, ):
        self.virtualization_and_dividers_matrix = self.virtualization_matrix * np.array(list(self.dividers.values()))[np.newaxis,:]
    
    def make_virt_setters(self, virtual_gates, elements):
        virtual_setters = {}
        for i, virt in enumerate(virtual_gates):
            for j, element in enumerate(elements):
                virtual_setters[f'{element}_{virt}'] = partial(self.set_virt_element, virtual_index=i, element=j) #lambda x: self.set_virt_element(
        return virtual_setters
    
    def make_virt_getters(self, virtual_gates, elements):
        virtual_getters = {}
        for i, virt in enumerate(virtual_gates):
            for j, element in enumerate(elements):
                virtual_getters[f'{element}_{virt}'] = partial(self.get_virt_element, virtual_index=i, element=j) #lambda x: self.set_virt_element(
        return virtual_getters

    def set_virtual1_range(self, value):
        self.virtual_ranges[0] = value / self.jump_amp 
        self.update = True

    def set_virtual2_range(self, value):
        self.virtual_ranges[1] = value / self.jump_amp
        self.update = True
    
    def set_resolution(self, value):
        assert value % 2 == 1, "the resolution must be odd {}".format(value)
        self.resolution = int(value)
        self.update = True

    def measurement_macro(self, ):
        if self.wait_time >= 4:  # if logic to enable wait_time = 0 without error
            wait(self.wait_time)

        measure(self.readout_pulse, self.measured_element, None, demod.full('cos', self._I), demod.full('sin', self._Q))
        save(self._I, self._I_stream)
        save(self._Q, self._Q_stream)

        if self.wait_time >= 4:  # if logic to enable wait_time = 0 without error
            wait(self.wait_time)


    def make_program(self,):

        ramp_to_zero_duration = 1
        div_resolution = 1/(self.resolution-1)
        # print(div_resolution)


        with program() as spiral_scan:
            # resolution_input_stream = declare_input_stream(int, name='resolution_input_stream')
            ranges_input_stream = declare_input_stream(fixed, name='ranges_input_stream', size=2)
            update_input_stream = declare_input_stream(bool, name='update_input_stream')
            virtualization_input_stream = declare_input_stream(fixed, name='virtualization_input_stream', size =len(self.elements)*2)

            virtual_steps = [declare(fixed), declare(fixed)]
            step_size_matrix = np.array([[declare(fixed) for i in range(len(self.elements))] for j in range(2)])


            i = declare(int)  # an index variable for the x index
            j = declare(int)  # an index variable for the y index

            gate_vals = {gate:declare(fixed, value=0) for gate in self.elements}
            gate_vals_streams = {gate:declare_stream() for gate in self.elements}

            moves_per_edge = declare(int)  # the number of moves per edge [1, resolution]
            completed_moves = declare(int)  # the number of completed move [0, resolution ** 2]
            movement_direction = declare(fixed)  # which direction to move {-1., 1.}

            # declaring the measured variables and their streams
            self._I, self._Q = declare(fixed), declare(fixed)
            self._I_stream, self._Q_stream = declare_stream(), declare_stream()

            with infinite_loop_():
                if self.run_test:
                    assign(virtual_steps[0], self.virtual_ranges[0]*div_resolution)
                    assign(virtual_steps[1], self.virtual_ranges[1]*div_resolution)
                    # print('ranges*div',self.virtual_ranges[0]*div_resolution, self.virtual_ranges[1]*div_resolution)

                    for k in range(2):
                        for l in range(len(self.elements)):
                                assign(step_size_matrix[k,l], self.virtualization_and_dividers_matrix[k,l] * virtual_steps[k])
                                # print(k, self.elements[l], self.virtualization_and_dividers_matrix[k,l] * self.virtual_ranges[k]*div_resolution )
                else:
                    advance_input_stream(update_input_stream)
                    with if_(update_input_stream):
                        # advance_input_stream(resolution_input_stream)
                        advance_input_stream(ranges_input_stream)
                        advance_input_stream(virtualization_input_stream)

                        # assign(resolution, resolution_input_stream)
                        # assign(div_resolution, Math.div(1, resolution-1))
                        assign(virtual_steps[0], ranges_input_stream[0]*div_resolution)
                        assign(virtual_steps[1], ranges_input_stream[1]*div_resolution)

                        for k in range(2):
                            for l in range(len(self.elements)):
                                assign(step_size_matrix[k,l], virtualization_input_stream[k*len(self.elements)+l] * virtual_steps[k])
                
                # initialising variables
                assign(moves_per_edge, 1)
                assign(completed_moves, 0)
                assign(movement_direction, +1)

                # for the first pixel it is unnecessary to move before measuring
                for gate in self.elements:
                    assign(gate_vals[gate], 0)
                    save(gate_vals[gate], gate_vals_streams[gate])

                if self.perform_measurement:
                    self.measurement_macro()
                
                with while_(completed_moves < self.resolution * (self.resolution - 1)):
                    # for_ loop to move the required number of moves in the x direction
                    with for_(i, 0, i < moves_per_edge, i + 1):
                        for gate, step_size in zip(self.elements, step_size_matrix[0,:]):
                            play(self.jump_pulse * amp(movement_direction * step_size), gate, duration=self.readout_pulse_length)
                            assign(gate_vals[gate], gate_vals[gate] + (movement_direction * step_size))
                            save(gate_vals[gate], gate_vals_streams[gate])

                        if self.perform_measurement:
                            self.measurement_macro()

                    # for_ loop to move the required number of moves in the y direction
                    with for_(j, 0, j < moves_per_edge, j + 1):
                        for gate, step_size in zip(self.elements, step_size_matrix[1,:]):
                            play(self.jump_pulse * amp(movement_direction * step_size), gate, duration=self.readout_pulse_length)
                            assign(gate_vals[gate], gate_vals[gate] + (movement_direction * step_size))
                            save(gate_vals[gate], gate_vals_streams[gate])

                        if self.perform_measurement:
                            self.measurement_macro()

                    # updating the variables
                    assign(completed_moves, completed_moves + 2 * moves_per_edge)  # * 2 because moves in both x and y
                    assign(movement_direction, movement_direction * -1)  # *-1 as subsequent steps in the opposite direction
                    assign(moves_per_edge, moves_per_edge + 1)  # moving one row/column out so need one more move_per_edge

                # filling in the final x row, which was not covered by the previous for_ loop
                with for_(i, 0, i < moves_per_edge - 1, i + 1):
                    for gate, step_size in zip(self.elements, step_size_matrix[0,:]):
                        play('CW'*amp(movement_direction * step_size), gate, duration=self.readout_pulse_length)
                        assign(gate_vals[gate], gate_vals[gate] + (movement_direction * step_size))
                        save(gate_vals[gate], gate_vals_streams[gate])

                    # Make sure that we measure after the pulse has settled
                    if self.perform_measurement:
                        self.measurement_macro()

                # aligning and ramping to zero to return to initial state
                for gate in self.elements:
                    ramp_to_zero(gate, duration = ramp_to_zero_duration)

                wait(1000)
            
            
            with stream_processing():
                if self.perform_measurement:
                    for stream_name, stream in zip(["I", "Q"], [self._I_stream, self._Q_stream]):
                        stream.buffer(self.resolution**2).save(stream_name) #.buffer(resolution**2)

                for gate, stream in gate_vals_streams.items():
                    stream.buffer(self.resolution**2).save_all(gate)

        return spiral_scan

    def send_input_streams(self,):
        self.running_job.insert_input_stream('ranges_input_stream', self.virtual_ranges)
        self.running_job.insert_input_stream('update_input_stream', [True])
        self.running_job.insert_input_stream('virtualization_input_stream', self.virtualization_and_dividers_matrix.flatten().tolist())
        # self.running_job.insert_input_stream('resolution_input_stream', self.resolution)


    def start_measurement(self, ):
        self.running_job = self.qm.execute(self.program)
        self.send_input_streams()
        sleep(5)
        # if self.perform_measurement:
        self.data_fetcher = fetching_tool(self.running_job, data_list=["I", "Q",], mode="live")
        # else:
        #     self.data_fetcher = None #fetching_tool(self.running_job, data_list = ['gate_7', 'gate_9', 'gate_10'], mode='live')
        print('REMEMBER TO END MEASUREMENT')
        

    def fetch_results(self, ):
        if hasattr(self, 'data_fetcher'):
            pass
        else:
            raise Exception('data fetcher not started, run "start_measurement" before trying to fetch results')
        
        if self.update:
            self.send_input_streams()
            self.update = False
        else:
            self.running_job.insert_input_stream('update_input_stream', [False])
        
        I, Q = self.data_fetcher.fetch_all()
        amplitude = I**2 + Q**2 
        self.order = spiral_order(self.resolution)
        return amplitude[self.order]

    def end_measurement(self, ):
        print(f"program ended: {self.running_job.halt()}")