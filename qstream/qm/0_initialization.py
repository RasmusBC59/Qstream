# -*- coding: utf-8 -*-
"""
Created on January 31 2023

@author: TLC
"""
import math
from time import strftime, localtime
import matplotlib.pyplot as plt
import numpy as np
import os
from time import sleep, monotonic
import qcodes as qc
from qcodes import Station, load_or_create_experiment, Measurement, load_by_run_spec, load_by_id, ManualParameter
from qcodes.dataset import initialise_or_create_database_at
from qcodes.dataset.plotting import plot_dataset, plot_by_id
from qcodes.dataset.data_set import load_by_id
from qcodes.utils.dataset.doNd import do0d,do1d, do2d
from datetime import datetime
import json
from opx_tools.opx_setup.saving import save_2d, save_1d
from copy import deepcopy
# qc.config.dataset.dond_plot = True

database_name = 'TLCTQD-5_T7_202406' #database name file. Look at cell below for its location

dir_database = 'F:\\database'
database_format = '.db'
database_path = os.path.join(dir_database, database_name + database_format)

qc.config.user.mainfolder = os.path.join(dir_database, database_name) #saves plots in png and pdf in the database folder
qc.logger.start_all_logging()
station = qc.Station()

qc.initialise_or_create_database_at(database_path)