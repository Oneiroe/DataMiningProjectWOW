"""
Algorithms to compute the similarity among characters
"""

import itertools
import time
import random
import math
import sys
import os
import logging
from tqdm import tqdm
import json


###############################################
# PREPROCESSING
##############


###############################################
# GENERAL DISTANCE FUNCTIONS
##############

def jaccard_distance(set_1, set_2):
    """ Jaccard distance is 1 minus the ratio of the sizes of the intersection and union of set_1 and set_2 """
    logging.debug('jaccard_distance(' + str(set_1) + ', ' + str(set_2) + ')')
    return 1 - len(set_1.intersection(set_2)) / len(set_1.union(set_2))


def hamming_distance(vector_1, vector_2):
    """ The Hamming distance between two vectors is the number of components in which they differ. """
    logging.debug('hamming_distance(' + str(vector_1) + ', ' + str(vector_2) + ')')
    if len(vector_1) != len(vector_2):
        raise ValueError('Different Vector Sizes')

    distance = len(vector_1)
    for i in range(len(vector_1)):
        if vector_1[i] == vector_2[i]:
            distance -= 1
    return distance


def euclidean_distance(vector_1, vector_2):
    """ The Euclidean distance (L2-norm) between two n-dimensional point is
    the square root of the sum of squares of the distances in each dimension """
    return math.sqrt(sum(pow(a - b, 2) for a, b in zip(vector_1, vector_2)))


###############################################
# CHARACTERS DISTANCE FUNCTIONS
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
    # distance = distance/8
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


# TODO pets can be consistently personalized
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


###############################################
# TEST-MAIN
##############
def main():
    pass


if __name__ == "__main__":
    main()
