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
import plotly
import plotly.graph_objs as go
from collections import Counter
import subprocess


###############################################
# UTILS
##############

def __r_plot(r_script_path, inputs, output_path):
    """ Launch externally a R plotting script """
    command = ['Rscript', r_script_path]
    for i in inputs:
        command += [i]
    command += [output_path]
    subprocess.call(args=command, shell=True)
    return


###############################################
# ITEMSETS
##############

##############
# preprocess

def __max_itemsets_number(unique_items, max_basket_length):
    """ Returns the max possible combination of items for each possible basket length """
    logging.debug('__max_itemsets_number')
    res = []
    f = math.factorial
    for i in range(1, max_basket_length + 1):
        # res += [len(list(itertools.combinations(unique_items, i)))]
        if unique_items >= i:
            res += [f(unique_items) // f(i) // f(unique_items - i)]
        else:
            res += [0]
    return res


def __itemsets_data_row_for_object(dat_itemsets_path):
    logging.debug('__itemsets_data_row_for_object()')
    # ORIGINAL ITEMSETS
    tot_distinct_items = set()
    num_itemsets = 0
    max_basket_length = 0  #
    baskets_len_distribution = []  # how many basket for each length
    with open(dat_itemsets_path, 'r') as input_file:
        reader = csv.reader(input_file, delimiter=' ')
        for row in reader:
            if len(row) == 0:
                continue
            num_itemsets += 1
            if row[-1] == '':
                row = row[:-1]
            for item in row:
                tot_distinct_items.add(item)
            if len(row) > max_basket_length:
                max_basket_length = len(row)
            baskets_len_distribution += [len(row)]
        baskets_len_distribution = Counter(baskets_len_distribution)
    # MAX combinations
    max_comb = __max_itemsets_number(len(tot_distinct_items), max_basket_length)
    return [tot_distinct_items, num_itemsets, max_basket_length, baskets_len_distribution, max_comb]


def __frequent_itemsets_data_row_for_object(dat_frequent_itemsets_path, max_basket_length):
    """ Retrun a csv containing the data ready to be plotted in R """
    logging.debug('__frequent_itemsets_data_row_for_object()')
    # FREQUENT ITEMSETS
    freq_distinct_items = set()
    frequent_itemsets_len_distribution = []
    frequent_distinct_items_per_length = [set() for _ in range(max_basket_length)]
    threshold = float(os.path.basename(dat_frequent_itemsets_path).split('[threshold_')[1][:-5])
    with open(dat_frequent_itemsets_path, 'r') as input_file:
        reader = csv.reader(input_file, delimiter=' ')
        for row in reader:
            if len(row) == 0:
                continue
            if row[-1] == '':
                row = row[:-1]
            for item in row:
                freq_distinct_items.add(item)
                frequent_distinct_items_per_length[len(row) - 1].add(item)
            frequent_itemsets_len_distribution += [len(row)]
        frequent_itemsets_len_distribution = Counter(frequent_itemsets_len_distribution)
    max_freq_comb = __max_itemsets_number(len(freq_distinct_items), max_basket_length)
    return [freq_distinct_items, frequent_itemsets_len_distribution, frequent_distinct_items_per_length, threshold,
            max_freq_comb]


def preprocess_itemsets_data(base_object_name, base_itemsets_path, base_frequent_itemsets_path, base_output_path):
    """ Return a CSV with the plotting-ready data about a particular itemsets category
    (e.g. total, specific_class, specific level, specific class and level, ...) """
    logging.info('preprocess_itemsets_data(' + base_object_name + ')')

    # original itemsets data
    i_data = __itemsets_data_row_for_object(os.path.join(base_itemsets_path, base_object_name + '.dat'))

    # data for each threshold
    with open(os.path.join(base_output_path, base_object_name + '.csv'), 'w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        header = ['file', 'threshold', 'distinct_items', 'itemsets', 'characters_threshold']
        # threshhold; number of distinct items; number of itemsets; threshold as number of character
        for i in range(1, i_data[2] + 1):
            header += ['itemsets_' + str(i)]
            # numper of itemsets where length=i
        for i in range(1, i_data[2] + 1):
            header += ['frequent_itemsets_' + str(i)]
            # numper of frequent itemsets where length=i
        for i in range(1, i_data[2] + 1):
            header += ['frequent_items_' + str(i)]
            # numper of frequent distinct items up to itemsets of length=i
        for i in range(1, i_data[2] + 1):
            header += ['combinations_items_' + str(i)]
            # numper of combination of distinct items of length=i
        for i in range(1, i_data[2] + 1):
            header += ['combinations_frequent_items_' + str(i)]
            # numper of combination of distinct frequent items of length=i

        writer.writerow(header)

        for f in os.listdir(base_frequent_itemsets_path):
            if base_object_name + '[' in f:
                f_data = __frequent_itemsets_data_row_for_object(os.path.join(base_frequent_itemsets_path, f),
                                                                 max_basket_length=i_data[2])
                row = [f, f_data[3], len(i_data[0]), i_data[1], int(f_data[3] * i_data[1])]
                # threshhold; number of distinct items; number of itemsets
                for i in range(1, i_data[2] + 1):
                    row += [i_data[3][i]]
                    # numper of itemsets where length=i
                for i in range(1, i_data[2] + 1):
                    row += [f_data[1][i]]
                    # numper of frequent itemsets where length=i
                for i in range(i_data[2]):
                    row += [len(f_data[2][i])]
                    # numper of frequent distinct items up to itemsets of length=i
                for i in range(i_data[2]):
                    row += [i_data[4][i]]
                    # numper of combination of distinct items of length=i
                for i in range(i_data[2]):
                    row += [f_data[4][i]]
                    # numper of combination of distinct frequent items of length=i

                writer.writerow(row)

    return


##############
# R

def plot_itemsets_stacked_area(itemset_data_plot_csv_path, output_path):
    """ Launch an R script to plot the stacked area graph for the give itemsets category """
    r_script_path = os.path.join(os.getcwd(), 'WOWanalysis', 'Rscripts', 'itemsets_stacked_area.r')
    inputs = [itemset_data_plot_csv_path]
    __r_plot(r_script_path, inputs, output_path)
    return


def plot_treemap_area(itemset_data_plot_csv_path, output_path):
    """ Launch an R script to plot the treemap graph for the give itemsets category """
    r_script_path = os.path.join(os.getcwd(), 'WOWanalysis', 'Rscripts', 'itemsets_treemap.r')
    inputs = [itemset_data_plot_csv_path]
    __r_plot(r_script_path, inputs, output_path)
    return


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


##############
# R

def plot_similarity_heatmap(distance_matrix_csv_path, output_path):
    """ Launch an R script to plot the heatmap for the give distance matrix """
    r_script_path = os.path.join(os.getcwd(), 'WOWanalysis', 'Rscripts', 'similarity_heatmap.r')
    inputs = [distance_matrix_csv_path]
    __r_plot(r_script_path, inputs, output_path)
    return


def plot_similarity_dendogram_heatmap(distance_matrix_csv_path, output_path):
    """ Launch an R script to plot the the heatmap for the give distance matrix reordering according hierarchies """
    r_script_path = os.path.join(os.getcwd(), 'WOWanalysis', 'Rscripts', 'similarity_dendogram_heatmap.r')
    inputs = [distance_matrix_csv_path]
    __r_plot(r_script_path, inputs, output_path)
    return


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

    ###############################################
    # ITEMSETS
    ##############

    # os.chdir(os.path.join(os.getcwd(), 'Results', 'test', 'plotly'))

    # preprocess_itemsets_data(
    #     'itemsets_unique_c3',
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'itemsets_unique'),
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'frequents_unique'),
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs')
    # )

    # preprocess itemsets
    # with tqdm(total=len(
    #         os.listdir(os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'itemsets_unique')))) as pbar:
    #     for f in os.listdir(os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'itemsets_unique')):
    #         pbar.update(1)
    #         if f.endswith('.dat'):
    #             preprocess_itemsets_data(
    #                 f.replace('.dat', ''),
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'itemsets_unique'),
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'frequents_unique'),
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs')
    #             )

    # plot all preprocessed itemsets

    # print("stacked area")
    # plot_itemsets_stacked_area(
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs', 'itemsets_unique_c4.csv'),
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs'))

    # print("treemap")
    # plot_treemap_area(
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs', 'itemsets_unique_c4.csv'),
    #     os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs'))

    # with tqdm(total=len(os.listdir(os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs')))) as pbar:
    #     for f in os.listdir(os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs')):
    #         pbar.update(1)
    #         if f.endswith('.csv'):
    #             logging.info(f)
    #             plot_itemsets_stacked_area(
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs', f),
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs'))
    #             plot_treemap_area(
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs', f),
    #                 os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'graphs'))

    ###############################################
    # SIMILARITY
    ##############

    # print('heatmap')
    # plot_similarity_heatmap(
    #     os.path.join(os.getcwd(), 'Results', 'similarity', 'sorted_matrix_unique_c12_lv100[appearance].csv'),
    #     os.path.join(os.getcwd(), 'Results', 'similarity', 'graphs'))
    # print('dendogram')
    # plot_similarity_dendogram_heatmap(
    #     os.path.join(os.getcwd(), 'Results', 'similarity', 'sorted_matrix_unique_c12_lv100[appearance].csv'),
    #     os.path.join(os.getcwd(), 'Results', 'similarity', 'graphs'))

    with tqdm(total=len(os.listdir(os.path.join(os.getcwd(), 'Results', 'similarity')))) as pbar:
        for f in os.listdir(os.path.join(os.getcwd(), 'Results', 'similarity')):
            pbar.update(1)
            if f.endswith('.csv'):
                logging.info(f)
                plot_similarity_heatmap(
                    os.path.join(os.getcwd(), 'Results', 'similarity', f),
                    os.path.join(os.getcwd(), 'Results', 'similarity', 'graphs'))
                plot_similarity_dendogram_heatmap(
                    os.path.join(os.getcwd(), 'Results', 'similarity', f),
                    os.path.join(os.getcwd(), 'Results', 'similarity', 'graphs'))


if __name__ == "__main__":
    main()
