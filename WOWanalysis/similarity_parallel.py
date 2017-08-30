"""
Algorithms to compute the similarity among characters
"""

import time
import math
import sys
import os
import logging
from tqdm import tqdm
import csv
import numpy as np
import pickle
import multiprocessing
from multiprocessing import Process, Pool, Value, Array, Lock, current_process
import psutil

# TODO generate single files containing all the items, pets , mounts,... so to speed up processing
###############################################
# GENERAL DISTANCE FUNCTIONS
##############

def jaccard_distance(set_1, set_2):
    """ Jaccard distance is 1 minus the ratio of the sizes of the intersection and union of set_1 and set_2 """
    # logging.debug('jaccard_distance(' + str(set_1) + ', ' + str(set_2) + ')')
    inter_dim = len(set_1.intersection(set_2))
    union_dim = len(set_1) + len(set_2) - inter_dim
    # union_dim = len(set_1.union(set_2))
    if union_dim == 0:
        return 0
    else:
        return 1 - inter_dim / union_dim
        # return 1 - len(set_1.intersection(set_2)) / union_dim
        # except ZeroDivisionError:
        #     return 0


def hamming_distance(vector_1, vector_2):
    """ The Hamming distance between two vectors is the number of components in which they differ. """
    # logging.debug('hamming_distance(' + str(vector_1) + ', ' + str(vector_2) + ')')

    # len(vector_1)==len(vector_2)==8
    distance = 8
    # if distance != len(vector_2):
    #     raise ValueError('Different Vector Sizes')
    for i in range(distance):
        if vector_1[i] == vector_2[i]:
            distance -= 1
    return distance


def euclidean_distance(vector_1, vector_2):
    """ The Euclidean distance (L2-norm) between two n-dimensional point is
    the square root of the sum of squares of the distances in each dimension """
    return math.sqrt(sum(pow(a - b, 2) for a, b in zip(vector_1, vector_2)))


def euclidean_distance_normalized(stats_1, stats_2, max_distance):
    """ Normalized Euclidean distance according to max stats found in the dataset. Returns value between 0 and 1 """
    # euclidean distance normalized over the maximal distance possible
    # distance = math.sqrt(sum(pow(a - b, 2) for a, b in zip(stats_1, stats_2)))
    distance = np.linalg.norm(stats_1 - stats_2)
    # if max_distance != 0:
    #     distance = distance / max_distance
    return distance / max_distance


###############################################
# CHARACTERS DISTANCE FUNCTIONS from serialized map
##############
def distance_general_from_map(character_1_map, character_2_map):
    """ Return the average distance measure between the two given characters according to all the defined distances
    opening the files just once """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 7  # how many distance functions are used

    # APPEARANCE
    # len(character_1_map['appearance'])==8
    distance += hamming_distance(character_1_map['appearance'], character_2_map['appearance']) / 8

    # ITEMS
    distance += jaccard_distance(character_1_map['items'], character_2_map['items'])

    # MOUNTS
    distance += jaccard_distance(character_1_map['mounts'], character_2_map['mounts'])

    # PETS
    distance += jaccard_distance(character_1_map['pets'], character_2_map['pets'])

    # PROFESSIONS
    distance += jaccard_distance(character_1_map['professions'], character_2_map['professions'])

    # STATS (normalized)
    distance += euclidean_distance_normalized(character_1_map['stats'],
                                              character_2_map['stats'],
                                              max_distance=5990271.526328605)

    # TALENTS
    distance += jaccard_distance(character_1_map['talents'], character_2_map['talents'])

    return distance / distance_dimensions


###############################################
# ANALYSIS
##############
# SEQUENTIAL
def distance_matrix_sequential(characters_list, distance_function, output_path):
    """ Write a file containing the distance matrix (triangle) """
    logging.debug('distance_matrix_sequential()')

    characters_num = len(characters_list)
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        # writer.writerow([None] + [os.path.basename(x) for x in characters_list])
        with tqdm(total=characters_num) as pbar:
            for i in range(characters_num):
                pbar.update(1)
                # out_line = [os.path.basename(characters_list[i])] + [None for j in range(i)]
                out_line = [None for j in range(i)]
                for j in range(i, characters_num):
                    out_line += [distance_function(characters_list[i], characters_list[j])]
                writer.writerow(out_line)
    return


##############
# Multi Process

def worker_row(i, characters_list, distance_function, output_queue):
    row = [None] * i
    for j in range(i, len(characters_list)):
        row += [distance_function(characters_list[i], characters_list[j])]
    output_queue.put(row)
    return row


def output_writer_listener(output_path, output_queue, characters_num):
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        with tqdm(total=characters_num) as pbar_out:
            writer = csv.writer(output_file)
            while 1:
                m = output_queue.get()
                if m == 'kill':
                    break
                writer.writerow(m)
                output_file.flush()
                pbar_out.update(1)


def distance_matrix_multi(characters_list, distance_function, output_path):
    """ Write distance matrix in parallel """
    logging.info('distance_matrix_multi()')
    manager = multiprocessing.Manager()
    output_queue = manager.Queue()
    # with Pool(multiprocessing.cpu_count()) as p:
    with Pool(4) as p:
        watcher = p.apply_async(output_writer_listener, (output_path, output_queue, len(characters_list)))
        row_pair_generator = ((i,
                               characters_list,
                               distance_function,
                               output_queue) for i in range(len(characters_list)))
        p.starmap(worker_row, row_pair_generator)
    return


######
# Multi bo


###############################################

###############################################
# TEST-MAIN
##############
def main():
    ###############################################
    ####
    # LOG setup
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'similarity_parallel_INFO.log'),
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

    # with open(os.path.join(os.getcwd(), 'Results', 'serialized_character_map_numpy.pickle'), 'rb') as f:
    with open(os.path.join(os.getcwd(),
                           'Results',
                           'PICKLES',
                           'serialized_character_map_numpy_unique.pickle'), 'rb') as f:
        characters_map = pickle.load(f)
    # characters_list = list(characters_map.values())[:2000]
    characters_list = list(characters_map.values())
    # characters_map = None  # space saving
    del characters_map  # space saving
    logging.info('Pickle dataset Loaded')
    print('characters_list (bytes): ' + str(sys.getsizeof(characters_list)))
    # print('Loading Time:' + str(time.time() - t))
    tstamp = time.time()
    # distance_matrix_sequential(characters_list, distance_general_from_map, 'test_matrix.csv')
    distance_matrix_multi(characters_list, distance_general_from_map, 'test_matrix.csv')

    #     wolfram alpha folmula for expectation, where sec=avg second to complete a full row
    #     sum (n/(235888/x)), 1<=n<=235888,x=20
    logging.info('END')
    logging.info('Time:' + str(time.time() - tstamp))
    logging.info('#################################################################################################')


if __name__ == "__main__":
    main()
