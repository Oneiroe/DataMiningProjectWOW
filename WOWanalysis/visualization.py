"""
Functions to plot analyses results
"""

import time
import math
import sys
import os
import numpy as np
import matplotlib.pyplot as mpl
import pandas
import logging
from tqdm import tqdm
import json
import csv
import pickle
import multiprocessing
from multiprocessing import Process, Pool, Value, Array, Lock, current_process
import psutil
import itertools
import random


###############################################
# SIMILARITY
##############

##############
# matplotlib
@DeprecationWarning
def show_distance_matrix_mpl(characters_iterator, distance_function):
    """ Compute a distance matrix on the fly and show it trough matPlotLib.
     ONLY FOR small data"""
    d = np.array([distance_function(x, y) for x in characters_iterator for y in characters_iterator])
    mpl.matshow(d.reshape(len(characters_iterator), len(characters_iterator)), cmap="Reds")
    mpl.colorbar()
    mpl.show()


def show_distance_matrix_from_file_mpl(csv_path):
    """ import a distance matrix from CSV and show it trough matPlotLib."""
    logging.info('show_distance_matrix_from_file_mpl')
    d = pandas.read_csv(csv_path)
    logging.info('loaded numpy matrix from csv')
    # mpl.matshow(d.reshape(len(characters_iterator), len(characters_iterator)), cmap="Reds")
    mpl.matshow(d, cmap="Reds")
    logging.info('created matplotlib object')
    mpl.colorbar()
    mpl.show()
    # mpl.savefig('test.png')


###############################################
# TEST-MAIN
##############
def main():
    ###############################################
    ####
    # LOG setup
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'visualization_INFO.log'),
                        level=logging.INFO,
                        format='%(asctime)-15s '
                               '%(levelname)s '
                               '--%(filename)s-- '
                               '%(message)s')

    DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')
    locations = {
        'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU'],
        'KR': ['ko_KR'],
        'TW': ['zh_TW'],
        'US': ['en_US', 'pt_BR', 'es_MX']
    }
    stats_max_dist_global = 5990271.526328605


if __name__ == "__main__":
    main()
