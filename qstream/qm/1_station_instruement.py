from opx_tools.opx_setup import OPX_Program_Parameter

STATION = qc.Station(config_file='Config_T7_acq_1_20231011.yaml', use_monitor=True)

qdac = STATION.load_instrument('qdacII_A')

dmm = STATION.load_instrument('keysight_A')

dmm_2 = STATION.load_instrument('keysight_B')

dmm_3 = STATION.load_instrument('keysight_C')

# dmm_RF = STATION.load_instrument('keysight_RF')

# ZNB = STATION.load_instrument('ZNB')

# SG = STATION.load_instrument('SG')

mag = STATION.load_instrument('magnet')

step_att = STATION.load_instrument('step_att_1')

# LK = STATION.load_instrument('Lockin_SR860')

opx_program = OPX_Program_Parameter()
STATION.add_component(opx_program)