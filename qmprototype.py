# %%
from qualang_tools.results import fetching_tool
from qm.qua import (wait_for_trigger,reset_phase,program,update_frequency, 
                   for_,stream_processing,declare,declare_stream,wait,measure,
                   play,save,fixed,demod,ramp,amp,if_,elif_,else_,align, ramp_to_zero, pause, assign, IO1, infinite_loop_)
import numpy as np
import matplotlib.pyplot as plt
import json
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import SimulationConfig

# %%

with open('qstream/qm/config_20230224_buffered.json','r') as file:
    config = json.load(file)
qmm=QuantumMachinesManager(host='10.209.66.187',port='80')
        #qmm.close_all_quantum_machines()
qm=qmm.open_qm(config, close_other_machines=True)
# %%
