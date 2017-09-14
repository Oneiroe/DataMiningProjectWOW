"""
Algorithms to compute the similarity among characters
"""

import time
import math
import sys
import os
import logging
from tqdm import tqdm
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import pickle
import multiprocessing
from multiprocessing import Process, Pool, Value, Array, Lock, current_process
import pandas
import psutil


###############################################
# PRE-PROCESSING
##############

def characters_stats_max_min_mean(DB_BASE_PATH, locations):
    """ Find the max, min and mean values of characters stats, looking in the whole dataset """
    logging.debug('characters_stats_max_min_mean()')
    maximum = {}
    minimum = {}
    mean = {}
    stats_num = 49 - 1
    # "powerType" is skipped
    characters_num = 0
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
                for file in os.listdir(CHARACTER_PATH):
                    pbar.update(1)
                    if not file.endswith('.json'):
                        continue
                    with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                        try:
                            character_json = json.load(character_file)
                            try:
                                characters_num += 1
                                for stat in character_json['stats']:
                                    if stat == 'powerType':
                                        continue
                                    maximum[stat] = max(maximum.setdefault(stat, character_json['stats'][stat]),
                                                        character_json['stats'][stat])
                                    minimum[stat] = min(minimum.setdefault(stat, character_json['stats'][stat]),
                                                        character_json['stats'][stat])
                                    mean[stat] = mean.setdefault(stat, 0) + character_json['stats'][stat]
                            except KeyError as err:
                                logging.warning(
                                    'KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                                logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                        except json.decoder.JSONDecodeError as err:
                            # Probable incomplete or wrongly downloaded data, retry
                            logging.warning(
                                'JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                            logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                            continue
    for stat in mean:
        mean[stat] = mean[stat] / characters_num

    # print(str(maximum))
    # print(str(minimum))
    # print(str(mean))
    with open(os.path.join('Results', 'character_max_stats.csv'), 'w', newline='', encoding='utf-8') as output:
        writer = csv.writer(output)
        writer.writerow(['STAT', 'MAX', 'MIN', 'MEAN'])
        for stat in maximum:
            writer.writerow([stat, maximum[stat], minimum[stat], mean[stat]])

    return maximum, minimum, mean


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


def canberra_distance(vector_1, vector_2):
    """ The Canberra distance between two n-dimensional point is
    the sum of the difference/summ of each dimension components"""

    return sum(abs(a - b) / (abs(a) + abs(b) + 0.000000000000000000000000000000001) for a, b in zip(vector_1, vector_2))


def canberra_distance_normalized(vector_1, vector_2):
    """ Camberra distance normalized over the number of vectors dimesions """
    n_dim = len(vector_1)
    return sum(abs(a - b) / (abs(a) + abs(b) + 0.0000000000000000000000001) for a, b in zip(vector_1, vector_2)) / n_dim


###############################################
# CHARACTERS DISTANCE FUNCTIONS directly from JSONs
##############

def distance_appearance(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "appearance" fields """
    logging.debug('distance_appearance(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                appearance_1 = character_1_json['appearance']
                appearance_2 = character_2_json['appearance']
                distance = hamming_distance(list(appearance_1.values()), list(appearance_2.values()))
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    # Normalization 0<=distance<=1
    distance = distance / len(list(appearance_1.values()))
    return distance


def distance_items(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "items" fields """
    logging.debug('distance_items(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                character_1_items = set()
                character_2_items = set()
                for field in character_1_json['items']:
                    if field in fields_to_skip:
                        continue
                    character_1_items.add(character_1_json['items'][field]['id'])
                for field in character_2_json['items']:
                    if field in fields_to_skip:
                        continue
                    character_2_items.add(character_2_json['items'][field]['id'])
                distance = jaccard_distance(character_1_items, character_2_items)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_mounts(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "mounts" fields """
    logging.debug('distance_mounts(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                character_1_mounts = set()
                character_2_mounts = set()
                for mount in character_1_json['mounts']['collected']:
                    character_1_mounts.add(mount['creatureId'])
                for mount in character_2_json['mounts']['collected']:
                    character_2_mounts.add(mount['creatureId'])
                distance = jaccard_distance(character_1_mounts, character_2_mounts)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_pets(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "pets" fields """
    logging.debug('distance_pets(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                character_1_pets = set()
                character_2_pets = set()
                for pet in character_1_json['pets']['collected']:
                    character_1_pets.add(pet['creatureId'])
                for pet in character_2_json['pets']['collected']:
                    character_2_pets.add(pet['creatureId'])
                distance = jaccard_distance(character_1_pets, character_2_pets)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_professions(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "professions" fields """
    logging.debug('distance_professions(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                character_1_professions = set()
                for primary_profession in character_1_json['professions']['primary']:
                    character_1_professions.add(primary_profession['id'])
                for secondary_profession in character_1_json['professions']['secondary']:
                    character_1_professions.add(secondary_profession['id'])

                character_2_professions = set()
                for primary_profession in character_2_json['professions']['primary']:
                    character_2_professions.add(primary_profession['id'])
                for secondary_profession in character_2_json['professions']['secondary']:
                    character_2_professions.add(secondary_profession['id'])

                distance = jaccard_distance(character_1_professions, character_2_professions)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_stats(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "stats" fields """
    logging.debug('distance_stats(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                stats_1 = character_1_json['stats']
                stats_1.pop('powerType')
                stats_1 = list(stats_1.values())
                stats_2 = character_2_json['stats']
                stats_2.pop('powerType')
                stats_2 = list(stats_2.values())
                distance = euclidean_distance(stats_1, stats_2)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_stats_normalized(character_1_json_path, character_2_json_path, max_distance=5990271.526328605):
    """ Return the distance measure between the two given characters according to their "stats" fields """
    logging.debug('distance_stats(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                stats_1 = character_1_json['stats']
                stats_1.pop('powerType')
                stats_1 = list(stats_1.values())
                stats_2 = character_2_json['stats']
                stats_2.pop('powerType')
                stats_2 = list(stats_2.values())
                # Normalization 0<=distance<=1
                distance = euclidean_distance_normalized(stats_1, stats_2, max_distance)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_talents(character_1_json_path, character_2_json_path):
    """ Return the distance measure between the two given characters according to their "talents" fields """
    logging.debug('distance_talents(' + str(character_1_json_path) + ', ' + str(character_2_json_path) + ')')
    distance = 0.0
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                talents_1 = set()
                for category in character_1_json['talents']:
                    for talent in category['talents']:
                        if talent is not None:
                            talents_1.add(talent['spell']['id'])

                talents_2 = set()
                for category in character_2_json['talents']:
                    for talent in category['talents']:
                        if talent is not None:
                            talents_2.add(talent['spell']['id'])

                distance = jaccard_distance(talents_1, talents_2)
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    return distance


def distance_general(character_1_json_path, character_2_json_path):
    """ Return the average distance measure between the two given characters according to all the defined distances
    opening the files just once """
    # logging.debug('distance_general_one_pass(' + str(os.path.basename(character_1_json_path)) + ', ' + str(os.path.basename(character_2_json_path)) + ')')
    distance = 0.0
    distance_dimensions = 0  # how many distance functions are used

    # Utils
    items_fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}
    with open(os.path.join(character_1_json_path)) as character_1_file, open(
            os.path.join(character_2_json_path)) as character_2_file:
        try:
            character_1_json = json.load(character_1_file)
            character_2_json = json.load(character_2_file)
            try:
                # APPEARANCE
                appearance_1 = list(character_1_json['appearance'].values())
                appearance_2 = list(character_2_json['appearance'].values())

                distance += hamming_distance(appearance_1, appearance_2) / len(appearance_1)
                distance_dimensions += 1

                # ITEMS
                character_1_items = set()
                character_2_items = set()
                for field in character_1_json['items']:
                    if field in items_fields_to_skip:
                        continue
                    character_1_items.add(character_1_json['items'][field]['id'])
                for field in character_2_json['items']:
                    if field in items_fields_to_skip:
                        continue
                    character_2_items.add(character_2_json['items'][field]['id'])

                distance += jaccard_distance(character_1_items, character_2_items)
                distance_dimensions += 1

                # MOUNTS
                character_1_mounts = set()
                character_2_mounts = set()
                for mount in character_1_json['mounts']['collected']:
                    character_1_mounts.add(mount['creatureId'])
                for mount in character_2_json['mounts']['collected']:
                    character_2_mounts.add(mount['creatureId'])
                distance += jaccard_distance(character_1_mounts, character_2_mounts)
                distance_dimensions += 1

                # PETS
                character_1_pets = set()
                character_2_pets = set()
                for pet in character_1_json['pets']['collected']:
                    character_1_pets.add(pet['creatureId'])
                for pet in character_2_json['pets']['collected']:
                    character_2_pets.add(pet['creatureId'])

                distance += jaccard_distance(character_1_pets, character_2_pets)
                distance_dimensions += 1

                # PROFESSIONS
                character_1_professions = set()
                for primary_profession in character_1_json['professions']['primary']:
                    character_1_professions.add(primary_profession['id'])
                for secondary_profession in character_1_json['professions']['secondary']:
                    character_1_professions.add(secondary_profession['id'])

                character_2_professions = set()
                for primary_profession in character_2_json['professions']['primary']:
                    character_2_professions.add(primary_profession['id'])
                for secondary_profession in character_2_json['professions']['secondary']:
                    character_2_professions.add(secondary_profession['id'])

                distance += jaccard_distance(character_1_professions, character_2_professions)
                distance_dimensions += 1

                # STATS (normalized)
                stats_1 = character_1_json['stats']
                stats_1.pop('powerType')
                stats_1 = list(stats_1.values())
                stats_2 = character_2_json['stats']
                stats_2.pop('powerType')
                stats_2 = list(stats_2.values())

                distance += euclidean_distance_normalized(stats_1, stats_2, max_distance=5990271.526328605)
                distance_dimensions += 1

                # TALENTS
                talents_1 = set()
                for category in character_1_json['talents']:
                    for talent in category['talents']:
                        if talent is not None:
                            talents_1.add(talent['spell']['id'])

                talents_2 = set()
                for category in character_2_json['talents']:
                    for talent in category['talents']:
                        if talent is not None:
                            talents_2.add(talent['spell']['id'])

                distance += jaccard_distance(talents_1, talents_2)
                distance_dimensions += 1

            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            except ValueError as err:
                logging.warning('ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        except json.decoder.JSONDecodeError as err:
            # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

    return distance / distance_dimensions


###############################################
# CHARACTERS DISTANCE FUNCTIONS from serialized dict
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


def distance_appearance_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to appearance field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # APPEARANCE
    # len(character_1_map['appearance'])==8
    distance += hamming_distance(character_1_map['appearance'], character_2_map['appearance']) / 8

    return distance / distance_dimensions


def distance_items_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to items field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # ITEMS
    distance += jaccard_distance(character_1_map['items'], character_2_map['items'])

    return distance / distance_dimensions


def distance_mounts_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to mounts field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # MOUNTS
    distance += jaccard_distance(character_1_map['mounts'], character_2_map['mounts'])

    return distance / distance_dimensions


def distance_pets_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to pets field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # PETS
    distance += jaccard_distance(character_1_map['pets'], character_2_map['pets'])

    return distance / distance_dimensions


def distance_professions_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to professions field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # PROFESSIONS
    distance += jaccard_distance(character_1_map['professions'], character_2_map['professions'])

    return distance / distance_dimensions


def distance_stats_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to stats field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

    # STATS (normalized)
    distance += euclidean_distance_normalized(character_1_map['stats'],
                                              character_2_map['stats'],
                                              max_distance=5990271.526328605)

    return distance / distance_dimensions


def distance_talents_from_map(character_1_map, character_2_map):
    """ Return the distance measure between the two given characters according to talents field """
    # logging.debug('distance_general_from_map(' + str(os.path.basename(character_1_map)) + ', ' + str(os.path.basename(character_2_map)) + ')')
    distance = 0.0
    distance_dimensions = 1  # how many distance functions are used

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

def worker_row(i, characters_list, characters_num, distance_function, output_queue):
    row = [None] * i
    for j in range(i, characters_num):
        row += [distance_function(characters_list[i], characters_list[j])]
    output_queue.put(row)
    return row


def output_writer_listener(output_path, output_queue, characters_num):
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        with tqdm(total=characters_num) as pbar_out:
            writer = csv.writer(output_file)
            while 1:
                m = output_queue.get()
                if m == 'stop':
                    return
                writer.writerow(m)
                output_file.flush()
                pbar_out.update(1)


def distance_matrix_multi(characters_list, distance_function, output_path):
    """ Write distance matrix in parallel """
    logging.info('distance_matrix_multi()')
    characters_num = len(characters_list)
    manager = multiprocessing.Manager()
    output_queue = manager.Queue()
    # with Pool(multiprocessing.cpu_count()) as p:
    logging.info('Available Memory (Mb): ' + str(psutil.virtual_memory().available / (1024 * 1024)))
    logging.info('Process Size (Mb): ' + str(psutil.Process(os.getpid()).memory_info().rss / float(2 ** 20)))
    logging.info('#Process fitting in memory: ' + str(int((psutil.virtual_memory().available / (1024 * 1024)) / (
        psutil.Process(os.getpid()).memory_info().rss / float(2 ** 20))) + 1))
    process_number = min(multiprocessing.cpu_count(),
                         int((psutil.virtual_memory().available / (1024 * 1024)) / (
                             psutil.Process(os.getpid()).memory_info().rss / float(2 ** 20))) + 1
                         )
    with Pool(process_number) as p:
        watcher = p.apply_async(output_writer_listener, (output_path, output_queue, characters_num))
        row_pair_generator = ((i,
                               characters_list,
                               characters_num,
                               distance_function,
                               output_queue) for i in range(characters_num))
        p.starmap(worker_row, row_pair_generator)
        output_queue.put('stop')
        watcher.get()
    return


##############
# Multi Post-Processing

def sort_distance_matrix(original_csv_path, characters_list, output_path):
    """ Sort in the right order the multi processing result"""
    logging.info('sort_distance_matrix()')
    app_indices = {}
    characters_num = 0
    # Pass-1 build index
    with open(original_csv_path, 'r', newline='', encoding='utf-8') as input_file:
        reader = csv.reader(input_file, delimiter=',')
        for row in reader:
            app_indices[row.count('')] = characters_num
            # app_seek[row.count('')] = input_file.tell()
            characters_num += 1
        # Pass-2 write
        input_file.seek(0)
        with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            # make header with characters names
            header_writer = csv.writer(output_file)
            header_writer.writerow(x['file'] for x in characters_list)

            with tqdm(total=characters_num) as pbar:
                l = input_file.readlines()
                for i in range(characters_num):
                    pbar.update(1)
                    index = app_indices[i]
                    output_file.write(l[index])

    return


##############
# Launcher

def distance_matrices_set(pickle_path, distances, output_base_path, override=False):
    """ Compute distance matrices for the given DB in all the distance measures proposed.
     Override value state if a file should be override if already existing"""
    logging.info('distance_matrices_set(' + str(os.path.basename(pickle_path)) + ')')

    # input pickle
    with open(pickle_path, 'rb') as f:
        characters_map = pickle.load(f)
    characters_list = list(characters_map.values())
    characters_list.sort(key=lambda k: (k['class'], k['level']))
    del characters_map

    for d_function, str_dist in distances:
        logging.info(str_dist)
        print(str_dist)

        temp_output_file_name = 'matrix_' + \
                                os.path.basename(pickle_path)[:-7].replace('serialized_character_map_numpy_', '') + \
                                '[' + str_dist + ']' + \
                                '.csv'
        output_file_name = 'sorted_matrix_' + \
                           os.path.basename(pickle_path)[:-7].replace('serialized_character_map_numpy_', '') + \
                           '[' + str_dist + ']' + \
                           '.csv'
        temp_path = os.path.join(output_base_path, temp_output_file_name)
        output_path = os.path.join(output_base_path, output_file_name)
        # check if already existing
        if not override and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            continue

        # create triangular distance matrix in multi process
        distance_matrix_multi(characters_list, d_function, temp_path)

        # sort triangular distance matrix
        sort_distance_matrix(temp_path, characters_list, output_path)

        # remove unsorted matrix
        os.remove(temp_path)

    del characters_list
    return


###############################################
# TEST-MAIN
##############
def main():
    ###############################################
    ####
    # LOG setup
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'similarity_INFO.log'),
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

    # # with open(os.path.join(os.getcwd(), 'Results', 'serialized_character_map_numpy.pickle'), 'rb') as f:
    # locale = 'zh_TW'
    # c = '8-10'
    # lv = '100'
    # with open(os.path.join(os.getcwd(),
    #                        'Results',
    #                        'DBs',
    #                        'serialized_character_map_numpy_unique_c' + c + '_lv' + lv + '.pickle'), 'rb') as f:
    #     # 'serialized_character_map_numpy_unique_c' + c + '.pickle'), 'rb') as f:
    #     # 'serialized_character_map_numpy_unique_' + locale + '.pickle'), 'rb') as f:
    #     characters_map = pickle.load(f)
    # characters_list = list(characters_map.values())[:1000]
    # # characters_list = list(characters_map.values())
    # # characters_list.sort(key=lambda k: (k['class'], k['level']))
    # del characters_map  # space saving

    tstamp = time.time()
    # # distance_matrix_sequential(characters_list, distance_general_from_map, 'test_matrix.csv')
    distances = [
        (distance_general_from_map, 'general'),
        (distance_appearance_from_map, 'appearance'),
        (distance_items_from_map, 'items'),
        (distance_mounts_from_map, 'mounts'),
        (distance_pets_from_map, 'pets'),
        (distance_professions_from_map, 'professions'),
        (distance_stats_from_map, 'stats'),
        (distance_talents_from_map, 'talents')
    ]

    # distance_matrices_set(
    #     os.path.join(os.getcwd(), 'Results', 'DBs', 'serialized_character_map_numpy_global.pickle'),
    #     distances,
    #     os.path.join(os.getcwd(), 'Results', 'similarity')
    # )
    #
    # distance_matrices_set(
    #     os.path.join(os.getcwd(), 'Results', 'DBs', 'serialized_character_map_numpy_global_unique.pickle'),
    #     distances,
    #     os.path.join(os.getcwd(), 'Results', 'similarity')
    # )
    #
    # for region in locations:
    #     distance_matrices_set(
    #         os.path.join(os.getcwd(), 'Results', 'DBs', 'serialized_character_map_numpy_unique_' + region + '.pickle'),
    #         distances,
    #         os.path.join(os.getcwd(), 'Results', 'similarity')
    #     )

    # for lv in ['90', '100', '110']:
    #     distance_matrices_set(
    #         os.path.join(os.getcwd(), 'Results', 'DBs', 'serialized_character_map_numpy_unique_lv' + lv + '.pickle'),
    #         distances,
    #         os.path.join(os.getcwd(), 'Results', 'similarity')
    #     )

    for c in range(1, 13):
        distance_matrices_set(
            os.path.join(os.getcwd(), 'Results', 'DBs', 'serialized_character_map_numpy_unique_c' + str(c) + '.pickle'),
            distances,
            os.path.join(os.getcwd(), 'Results', 'similarity')
        )
        for lv in ['90', '100', '110']:
            distance_matrices_set(
                os.path.join(os.getcwd(), 'Results', 'DBs',
                             'serialized_character_map_numpy_unique_c' + str(c) + '_lv' + lv + '.pickle'),
                distances,
                os.path.join(os.getcwd(), 'Results', 'similarity')
            )

    # for d_function, str_dist in distances:
    #     print(str_dist)
    #     # create triangular distance matrix in multi process
    #     distance_matrix_multi(characters_list,
    #                           d_function,
    #                           os.path.join(os.getcwd(),
    #                                        'Results',
    #                                        'similarity',
    #                                        'matrix_c' + c + '_lv' + lv + '[' + str_dist + ']' + '.csv'))
    #     # 'matrix_c' + c + '[' + str_dist + ']' + '.csv'))
    #     # 'matrix_c' + locale + '[' + str_dist + ']' + '.csv'))
    #     # del characters_list
    #
    #     # sort triangular distance matrix
    #     sort_distance_matrix(os.path.join(os.getcwd(),
    #                                       'Results',
    #                                       'similarity',
    #                                       'matrix_c' + c + '_lv' + lv + '[' + str_dist + ']' + '.csv'),
    #                          # 'matrix_c' + c + '[' + str_dist + ']' + '.csv'),
    #                          # 'matrix_c' + locale + '[' + str_dist + ']' + '.csv'),
    #                          os.path.join(os.getcwd(),
    #                                       'Results',
    #                                       'similarity',
    #                                       'sorted_matrix_c' + c + '_lv' + lv + '[' + str_dist + ']' + '.csv'))
    #     # 'sorted_matrix_c' + c + '[' + str_dist + ']' + '.csv'))
    #     # 'sorted_matrix_c' + locale + '[' + str_dist + ']' + '.csv'))
    #
    #     # remove unsorted matrix
    #     os.remove(os.path.join(os.getcwd(),
    #                            'Results',
    #                            'similarity',
    #                            'matrix_c' + c + '_lv' + lv + '[' + str_dist + ']' + '.csv'))

    # wolfram alpha folmula for expectation, where sec=avg second to complete a full row
    #     sum (n/(235888/x)), 1<=n<=235888,x=20
    logging.info('END')
    logging.info('Time:' + str(time.time() - tstamp))

    logging.info('#################################################################################################')


if __name__ == "__main__":
    main()
