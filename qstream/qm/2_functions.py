# Data analysis

# gerneral plotting tools
def adjust_fontsize(title, fig_size):
    title_length = len(title)/3
    fig_width, fig_height = fig_size
    # Assuming some relation between figure size and title length
    font_size = min(18, int(30 * (fig_width + fig_height) / title_length))
    return font_size

# Coulomb peaks
def Coulomb_peaks_find_local_extremum(ID, type, x_min, x_max):
    dataset = load_by_id(ID)
    data_dict = dataset.get_parameter_data() 
    parameter_list = list(dataset.description.interdeps.names)
    x_index = 1
    y_index = 0
    x_axis_name = parameter_list[x_index]
    y_axis_name = parameter_list[y_index]

    x_data = data_dict[y_axis_name][x_axis_name]
    y_data = data_dict[y_axis_name][y_axis_name]

    # Define the range you want to extract
    x_min = -0.415
    x_max = -0.404

    # Find indices where x falls within the specified range
    indices = np.where((x_data >= x_min) & (x_data <= x_max))

    # Extract the subset of x and y based on the indices
    subset_x_data = x_data[indices]
    subset_y_data = y_data[indices]

    if type == "max":
        # Find the index of the peak
        term = "peak (max)"
        extremum_index = np.argmax(subset_y_data)
    elif type == "min":
        # Find the index of the dip
        term = "dip (min)"
        extremum_index = np.argmin(subset_y_data)
    else:
        print("Please define the extremum type: max or min")

    # Peak location
    extremum_location = subset_x_data[extremum_index]
    extremum_value = subset_y_data[extremum_index]
    print("%s position: x = %f, y = %e"%(term, extremum_location, extremum_value))
    return extremum_location

# Optimal freq 
def Reflectometry_find_optimal_freq(IDs, do_plot = True):
    dataset = load_by_id(IDs[0])
    data_dict = dataset.get_parameter_data() 
    parameter_list = list(dataset.description.interdeps.names)
    x_index = 1
    y_index = 0
    x_axis_name = parameter_list[x_index]
    y_axis_name = parameter_list[y_index]
    x_data_0 = data_dict[y_axis_name][x_axis_name]
    y_data_0 = data_dict[y_axis_name][y_axis_name]

    dataset = load_by_id(IDs[1])
    data_dict = dataset.get_parameter_data() 
    parameter_list = list(dataset.description.interdeps.names)
    x_index = 1
    y_index = 0
    x_axis_name = parameter_list[x_index]
    y_axis_name = parameter_list[y_index]

    x_data_1 = data_dict[y_axis_name][x_axis_name]
    y_data_1 = data_dict[y_axis_name][y_axis_name]

    y_data = abs(y_data_1 - y_data_0)
    extremum_index = np.argmax(y_data)
    extremum_location = x_data_0[extremum_index]

    # plotting
    if do_plot == True:
        # text settings
        title = 'T7_A TLCTQD-5 BR device'
        plot_x_axis_name = 'S21 frequency (MHz)'
        plot_y_axis_name = 'S21 magnitude (dB)'
        label_name = 'ID 176 - 177'
        # you can do data calculation here before you define the x and the y
        x = x_data_0/1e+6
        y = y_data
        # figure settings
        # font size
        font = 12

        # 1D plot
        fig1, ax1 = plt.subplots(figsize = (7,5))
        ax1.plot(x, y, color ="b", label = label_name)

        # legend, grid, title, tick lables
        ax1.legend(loc = "best", fontsize = font*0.8)
        ax1.set_xlabel(plot_x_axis_name, fontsize = font)
        ax1.set_ylabel(plot_y_axis_name, fontsize = font)
        ax1.grid(True)
        plt.title(title, fontsize = 1.5*font)
        plt.xticks(fontsize = font)
        plt.yticks(fontsize = font)
        plt.ticklabel_format(axis='both',style='sci')
        # save figure
        # plt.savefig(plot_save_name + '.png', facecolor='w')
        plt.show()
    
    print("The optimal freq: %e"%(extremum_location))
    return extremum_location





# spin funnel sequence related
def line_polor_info(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    # Calculate the slope
    m = (y2 - y1) / (x2 - x1)
    # Calculate the y-intercept
    b = y1 - m * x1

    R = ((y2 - y1)**2 + (x2 - x1)**2)**0.5
    angle = math.atan2(y2 - y1, x2 - x1)*180/np.pi
    return m, b, R, angle

def calculate_y(m, b, x):
    # Calculate the corresponding y value
    y = m * x + b
    return y

# step attenuator function
def step_att_attenuation_set(att_target):
    step_att.attenuation(att_target)
    while step_att.attenuation()!= att_target:
        sleep(0.01)
    print('successfully set the attenuation to ',att_target)
    for i in range(10):
        print(step_att.attenuation())

# magnet function
def seconds_to_hms(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:0.2f}"

def magnet_Bz_ramp(Bz_target, show_estimated_time = False, dummy_time_sweep = False):
    mag_rate = 0.0002

    print('Mag Bz: ramping to target: %.3f '%Bz_target)

    mag.GRPZ.field_ramp_rate(mag_rate) # 0.0002 T/s  = 0.012 T / min
    mag.z_target(Bz_target)
    mag.ramp(mode='simul')

    interval_time = 5
    est_time_in_secs = abs((Bz_target - mag.z_measured()))/mag_rate
    est_time_in_formate = seconds_to_hms(est_time_in_secs)
    mag_steps = round(est_time_in_secs/interval_time)+1 # extra 5 secs

    if show_estimated_time:
        print('Estimated time: %s'%est_time_in_formate)
    
    if dummy_time_sweep:
        dummy_time = qc.ManualParameter('dummy_time')
        do1d(dummy_time, 0, 1, mag_steps, interval_time, mag.z_measured)
    else:
        sleep(interval_time * mag_steps)

    print('Mag Bz:reached the target: %.3f'%mag.z_measured())
    
def magnet_Bx_ramp(Bx_target, show_estimated_time = False, dummy_time_sweep = False):
    mag_rate = 0.0002

    print('Mag Bx: ramping to target: %.3f '%Bx_target)

    mag.GRPX.field_ramp_rate(mag_rate) # 0.0002 T/s  = 0.012 T / min
    mag.x_target(Bx_target)
    mag.ramp(mode='simul')

    interval_time = 5
    est_time_in_secs = abs((Bx_target - mag.x_measured()))/mag_rate
    est_time_in_formate = seconds_to_hms(est_time_in_secs)
    mag_steps = round(est_time_in_secs/interval_time)+1 # extra 5 secs

    if show_estimated_time:
        print('Estimated time: %s'%est_time_in_formate)
    
    if dummy_time_sweep:
        dummy_time = qc.ManualParameter('dummy_time')
        do1d(dummy_time, 0, 1, mag_steps, interval_time, mag.x_measured)
    else:
        sleep(interval_time * mag_steps)

    print('Mag Bx:reached the target: %.3f'%mag.x_measured())
    
# LK function
def LK_transport_get():
      LK_I = LK.R()*1e-8
      LK_V = LK.amplitude()*1e-5
      LK_G = LK_I/LK_V
      G_quanta = 1/25812.80745 # e^2/h
      LK_G_quanta = LK_G/G_quanta
LK_G_quanta = qc.Parameter(name='AC_dI_dV_conductance',label='AC_dI_dV_conductance',unit='e^2/h', get_cmd=LK_transport_get)

# qcodes doNd template
def print_do1d_template():
    print("volt_start = \nvolt_target = \nsteps = \ninterval_time = \nqdac.BNC__(volt_start)\nsleep(2)\ndo1d(qdac.BNC__, volt_start, volt_target, steps, interval_time, __)")

# Ithaco function
def Ithaco_0_get():
    return dmm.volt()*1e-8*(-1)

Ithaco_SD_1_2 = qc.Parameter(name='Ithaco_SD_1_2',label='ohmic_2_BNC09',unit='A', get_cmd=Ithaco_0_get)

def Ithaco_1_get():
    return dmm_2.volt()*1e-8*(-1)

Ithaco_SD_3_4 = qc.Parameter(name='Ithaco_SD_3_4',label='ohmic_4_BNC40',unit='A', get_cmd=Ithaco_1_get)

def Ithaco_2_get():
    return dmm_3.volt()*1e-8*(-1)

Ithaco_SD_5_6 = qc.Parameter(name='Ithaco_SD_5_6',label='ohmic_5_BNC31',unit='A', get_cmd=Ithaco_2_get)

def all_Ithaco_print():
     curr_1 = Ithaco_SD_1_2()*1e+9
     curr_2 = Ithaco_SD_3_4()*1e+9
     curr_3 = Ithaco_SD_5_6()*1e+9
     print("ohmic 2 BNC09 current (A):%f"%curr_1)
     print("ohmic 4 BNC40 current (A):%f"%curr_2)
     print("ohmic 6 BNC24 current (A):%f"%curr_3)

# database function
def reset_default_db_file_path():
    database_name = 'TLCTQD-5_T7_202401' #database name file. Look at cell below for its location
    dir_database = 'F:\\database'
    database_format = '.db'
    database_path = os.path.join(dir_database, database_name + database_format)
    initialise_or_create_database_at(database_path)  

def do2d_substration_by_run_ID(ID_1, ID_2):
    ds = load_by_id(ID_1)
    a = ds.to_xarray_dataset()
    z1= a.amp.values

    ds = load_by_id(ID_2)
    a = ds.to_xarray_dataset()
    z2= a.amp.values

    plt.pcolormesh(np.abs((z2-z1)))

# QDAC control
def print_qdac_channels():
    for ch in qdac.channels:
        print(ch.name , ch.output_range())
        print(ch.name , ch.dc_constant_V())

def all_volt_control(value):
    for ch in qdac.channels:
        ch.dc_constant_V(value)
        print(ch.name , ch.dc_constant_V())  
              
def all_output_range_control(range_string: str):
    if range_string == 'low' or 'high':
        for ch in qdac.channels:
            ch.output_range(range_string)
            print(ch.name ,'output range has changed to', ch.output_range())
    else:
        print('Please select either low or high')   
         
def all_ch_step_inter_delay_set(step_size = 0.001, inter_delay_time = 0.001):
     for ch in qdac.channels:
          ch.dc_constant_V.step = step_size
          ch.dc_constant_V.inter_delay = inter_delay_time
          print(ch.name , 'step: ',ch.dc_constant_V.step, 
                ' inter_delay: ',ch.dc_constant_V.inter_delay) 


def QDac_voltage_show_history_based_on_run_ID(model, ID, db_file_address_name=None):
    if db_file_address_name == None:
        dataset = load_by_id(ID)
        snapshot_of_run_in_json_format = dataset.snapshot_raw
        snapshot_of_run_in_json_format_dict = json.loads(snapshot_of_run_in_json_format)
        if model == 'QDACII':
            for i, ch in enumerate(qdac.channels):
                channel_label = 'ch' + '%02d'%(i+1)
                dc_constant_V_value = snapshot_of_run_in_json_format_dict['station']['instruments']['qdacII_A']['submodules'][channel_label]['parameters']['dc_constant_V']['value']
                print("%s = %.6f V"%(channel_label, dc_constant_V_value))
        else:
            print("Please define the model: QDACII.")
    else:
        initialise_or_create_database_at(db_file_address_name)
        dataset = load_by_id(ID)
        snapshot_of_run_in_json_format = dataset.snapshot_raw
        snapshot_of_run_in_json_format_dict = json.loads(snapshot_of_run_in_json_format)
        if model == 'QDACII':
            for i, ch in enumerate(qdac.channels):
                channel_label = 'ch' + '%02d'%(i+1)
                dc_constant_V_value = snapshot_of_run_in_json_format_dict['station']['instruments']['qdacII_A']['submodules'][channel_label]['parameters']['dc_constant_V']['value']
                print("%s = %.6f V"%(channel_label, dc_constant_V_value))
        else:
            print("Please define the model: QDACII.")
        reset_default_db_file_path()
    

def QDac_voltage_restore_based_on_run_ID(model, ID):
    dataset = load_by_id(ID)
    snapshot_of_run_in_json_format = dataset.snapshot_raw
    snapshot_of_run_in_json_format_dict = json.loads(snapshot_of_run_in_json_format)
    if model == 'QDACII':
          for i, ch in enumerate(qdac.channels):
               channel_label = 'ch' + '%02d'%(i+1)
               dc_constant_V_value = snapshot_of_run_in_json_format_dict['station']['instruments']['qdacII_A']['submodules'][channel_label]['parameters']['dc_constant_V']['value']
               ch.dc_constant_V.inter_delay = 0.001
               ch.dc_constant_V.step = 0.001
               ch.dc_constant_V(dc_constant_V_value)
               print("Set %s to %.6f V"%(channel_label, dc_constant_V_value))
    else:
         print("Please define the model: QDACII.")
               
    

def QDac_voltage_restore_based_on_snapshot(model, name):
    file_name = 'N:\SCI-NBI-QDev\Tsung-Lin\Project\Measurement\T7\qcodes\QDAC_snapshot\\' + str(name) + '.dat'
    with open(file_name, 'r') as f:
        QDAC_voltages_list = f.readlines()

    for i, volt in enumerate(QDAC_voltages_list):
        QDAC_voltages_list[i] = float(volt.strip('\n'))

    if  model == 'QDACII':
        for i, ch in enumerate(qdac.channels):
            ch.dc_constant_V.inter_delay = 0.001
            ch.dc_constant_V.step = 0.001
            ch.dc_constant_V(QDAC_voltages_list[i])
            print("Set ch%02d to %.6f V"%((i+1), QDAC_voltages_list[i]))
    elif model == "QDEVQDAC":
        for i, ch in enumerate(qdac.channels):
            ch.v.inter_delay = 0.001
            ch.v.step = 0.001
            ch.v(QDAC_voltages_list[i])
            print("Set ch%02d to %.6f V"%((i+1), QDAC_voltages_list[i]))
    else:
         print("Please define the model: QDACII or QDEVQDAC.")

def QDac_voltages_snapshot(model, name):
    if model == 'QDACII':
        voltage_list = qdac.channels.dc_constant_V()
    elif model == "QDEVQDAC":
        voltage_list = qdac.channels.v()
    else:
        print('Please define a model name')
        return None
    timestamp = strftime("%Y-%m-%d_%H_%M_%S", localtime())
    file_name = 'N:\SCI-NBI-QDev\Tsung-Lin\Project\Measurement\T7\qcodes\QDAC_snapshot\\' + str(name) + '_%s.dat'%timestamp
    with open(file_name, 'a') as f:
        for volt in voltage_list:
            f.write(f'{volt}\n')
    print('File saved at ' + file_name)

# TLCTQD gate control
def allohmics_set(volt):
    qdac.ohmic_1(volt)
    qdac.ohmic_3(volt)
    qdac.ohmic_5(volt)
allohmics = qc.Parameter(name='allohmics',label='allohmics',unit='V', set_cmd=allohmics_set)

    

def allgates_set(volt):
	qdac.BNC11(volt)
	qdac.BNC10(volt)
	qdac.BNC08(volt)
	qdac.BNC47(volt)
	qdac.BNC43(volt)
	qdac.BNC42(volt)
	qdac.BNC30(volt)
	qdac.BNC29(volt)
	qdac.BNC25(volt)
	qdac.BNC06(volt)
	qdac.BNC20(volt)
	qdac.BNC07(volt)
	qdac.BNC05(volt)
	qdac.BNC48(volt)
	qdac.BNC37(volt)
	qdac.BNC36(volt)
	qdac.BNC34(volt)
	qdac.BNC32(volt)
	qdac.BNC21(volt)
	qdac.BNC12(volt)
	qdac.BNC19(volt)
allgates = qc.Parameter(name='allgates',label='allgates',unit='V', set_cmd=allgates_set)

def allgates_wo_all_SET_gate_set(volt):
	qdac.BNC06(volt)
	qdac.BNC20(volt)
	qdac.BNC07(volt)
	qdac.BNC05(volt)
	qdac.BNC48(volt)
	qdac.BNC37(volt)
	qdac.BNC36(volt)
	qdac.BNC34(volt)
	qdac.BNC32(volt)
	qdac.BNC21(volt)
	qdac.BNC12(volt)
	qdac.BNC19(volt)
allgates_wo_all_SET_gate = qc.Parameter(name='allgates_wo_all_SET_gate',label='allgates_wo_all_SET_gate',unit='V', set_cmd=allgates_wo_all_SET_gate_set)

def allgates_wo_top_SET_set(volt):
	qdac.BNC47(volt)
	qdac.BNC43(volt)
	qdac.BNC42(volt)
	qdac.BNC30(volt)
	qdac.BNC29(volt)
	qdac.BNC25(volt)
	qdac.BNC06(volt)
	qdac.BNC20(volt)
	qdac.BNC07(volt)
	qdac.BNC05(volt)
	qdac.BNC48(volt)
	qdac.BNC37(volt)
	qdac.BNC36(volt)
	qdac.BNC34(volt)
	qdac.BNC32(volt)
	qdac.BNC21(volt)
	qdac.BNC12(volt)
	qdac.BNC19(volt)
allgates_wo_top_SET = qc.Parameter(name='allgates_wo_top_SET',label='allgates_wo_top_SET',unit='V', set_cmd=allgates_wo_top_SET_set)

def allgates_wo_left_SET_set(volt):
	qdac.BNC11(volt)
	qdac.BNC10(volt)
	qdac.BNC08(volt)
	qdac.BNC30(volt)
	qdac.BNC29(volt)
	qdac.BNC25(volt)
	qdac.BNC06(volt)
	qdac.BNC20(volt)
	qdac.BNC07(volt)
	qdac.BNC05(volt)
	qdac.BNC48(volt)
	qdac.BNC37(volt)
	qdac.BNC36(volt)
	qdac.BNC34(volt)
	qdac.BNC32(volt)
	qdac.BNC21(volt)
	qdac.BNC12(volt)
	qdac.BNC19(volt)
allgates_wo_left_SET = qc.Parameter(name='allgates_wo_left_SET',label='allgates_wo_left_SET',unit='V', set_cmd=allgates_wo_left_SET_set)

def allgates_wo_right_SET_set(volt):
	qdac.BNC11(volt)
	qdac.BNC10(volt)
	qdac.BNC08(volt)
	qdac.BNC47(volt)
	qdac.BNC43(volt)
	qdac.BNC42(volt)
	qdac.BNC06(volt)
	qdac.BNC20(volt)
	qdac.BNC07(volt)
	qdac.BNC05(volt)
	qdac.BNC48(volt)
	qdac.BNC37(volt)
	qdac.BNC36(volt)
	qdac.BNC34(volt)
	qdac.BNC32(volt)
	qdac.BNC21(volt)
	qdac.BNC12(volt)
	qdac.BNC19(volt)
allgates_wo_right_SET = qc.Parameter(name='allgates_wo_right_SET',label='allgates_wo_right_SET',unit='V', set_cmd=allgates_wo_right_SET_set)

def top_SET_gates_set(volt):
	qdac.BNC11(volt)
	qdac.BNC10(volt)
	qdac.BNC08(volt)
top_SET_gates_BNC_11_10_08 = qc.Parameter(name='top_SET_gates_BNC_11_10_08',label='top_SET_gates_BNC_11_10_08',unit='V', set_cmd=top_SET_gates_set)

def left_SET_gates_set(volt):
	qdac.BNC47(volt)
	qdac.BNC43(volt)
	qdac.BNC42(volt)
left_SET_gates_BNC_47_43_42 = qc.Parameter(name='left_SET_gates_BNC_47_43_42',label='left_SET_gates_BNC_47_43_42',unit='V', set_cmd=left_SET_gates_set)

def right_SET_gates_set(volt):
	qdac.BNC30(volt)
	qdac.BNC29(volt)
	qdac.BNC25(volt)
right_SET_gates_BNC_30_29_25 = qc.Parameter(name='right_SET_gates_BNC_30_29_25',label='right_SET_gates_BNC_30_29_25',unit='V', set_cmd=right_SET_gates_set)

def top_pair_confinement_set(volt):
	qdac.BNC06(volt)
	qdac.BNC20(volt)
top_pair_confinement_BNC_06_20 = qc.Parameter(name='top_pair_confinement_BNC_06_20',label='top_pair_confinement_BNC_06_20',unit='V', set_cmd=top_pair_confinement_set)

def left_pair_confinement_set(volt):
	qdac.BNC48(volt)
	qdac.BNC37(volt)
left_pair_confinement_BNC_48_37 = qc.Parameter(name='left_pair_confinement_BNC_48_37',label='left_pair_confinement_BNC_48_37',unit='V', set_cmd=left_pair_confinement_set)

def right_pair_confinement_set(volt):
	qdac.BNC32(volt)
	qdac.BNC21(volt)
right_pair_confinement_BNC_32_21 = qc.Parameter(name='right_pair_confinement_BNC_32_21',label='right_pair_confinement_BNC_32_21',unit='V', set_cmd=right_pair_confinement_set)

def top_pair_barrier_set(volt):
	qdac.BNC05(volt)
	qdac.BNC19(volt)
top_pair_barrier_BNC_05_19 = qc.Parameter(name='top_pair_barrier_BNC_05_19',label='top_pair_barrier_BNC_05_19',unit='V', set_cmd=top_pair_barrier_set)

def left_pair_barrier_set(volt):
	qdac.BNC05(volt)
	qdac.BNC34(volt)
left_pair_barrier_BNC_05_34 = qc.Parameter(name='left_pair_barrier_BNC_05_34',label='left_pair_barrier_BNC_05_34',unit='V', set_cmd=left_pair_barrier_set)

def right_pair_barrier_set(volt):
	qdac.BNC34(volt)
	qdac.BNC19(volt)
right_pair_barrier_BNC_34_19 = qc.Parameter(name='right_pair_barrier_BNC_34_19',label='right_pair_barrier_BNC_34_19',unit='V', set_cmd=right_pair_barrier_set)


def all_barrier_set(volt):
    qdac.BNC05(volt)
    qdac.BNC34(volt)
    qdac.BNC19(volt)
all_barrier_BNC_05_34_19 = qc.Parameter(name='all_barrier_BNC_05_34_19',label='all_barrier_BNC_05_34_19',unit='V', set_cmd=all_barrier_set)