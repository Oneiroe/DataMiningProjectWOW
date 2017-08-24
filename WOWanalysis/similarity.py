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
import csv
import numpy as np
import matplotlib.pyplot as plt


###############################################
# PREPROCESSING
##############

def characters_stats_max_min_mean(DB_BASE_PATH, locations):
    """ Find the max, min and mean values of characters stats, looking in the whole dataset """
    logging.debug('characters_stats_max_min_mean()')
    maximum = {}
    minimum = {}
    mean = {}
    stats_num = 49 - 1
    characters_num = 0
    # "powerType" is skipped
    for nation in locations:
        for locale in locations[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
    logging.debug('jaccard_distance(' + str(set_1) + ', ' + str(set_2) + ')')
    if len(set_1.union(set_2)) == 0:
        return 0
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


def euclidean_distance_normalized(stats_1, stats_2, max_distance):
    """ Normalized Euclidean distance according to max stats found in the dataset. Returns value between 0 and 1 """
    # euclidean distance normalized over the maximal distance possible
    distance = math.sqrt(sum(pow(a - b, 2) for a, b in zip(stats_1, stats_2)))
    if max_distance != 0:
        distance = distance / max_distance
    return distance


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


# TODO pets can be consistently personalized, not just owned
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


###############################################
# VISUALIZATION
##############
def show_distance_matrix(characters_iterator, distance_function):
    d = np.array([distance_function(x, y) for x in characters_iterator for y in characters_iterator])
    plt.matshow(d.reshape(len(characters_iterator), len(characters_iterator)), cmap="Reds")
    plt.colorbar()
    plt.show()


###############################################
# TEST-MAIN
##############
def main():
    ###############################################
    ####
    # LOG setup
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'similarity_DEBUG.log'),
                        level=logging.DEBUG,
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

    # maximum, minimum, mean = characters_stats_max_min_mean(DB_BASE_PATH, locations)
    stats_maximum_global = {'agi': 44923, 'armor': 78232, 'avoidanceRating': 892.0, 'avoidanceRatingBonus': 20.0,
                      'block': 129.9673, 'blockRating': 0, 'crit': 134.29715, 'critRating': 24400, 'dodge': 1103.7595,
                      'dodgeRating': 11543, 'haste': 132.06, 'hasteRating': 19220, 'hasteRatingPercent': 115.55567,
                      'health': 5693023, 'int': 46425, 'leech': 102.430435, 'leechRating': 878.0,
                      'leechRatingBonus': 20.25, 'mainHandDmgMax': 100274.0, 'mainHandDmgMin': 90031.0,
                      'mainHandDps': 58630.99, 'mainHandSpeed': 3.8, 'mana5': 148265.0, 'mana5Combat': 148265.0,
                      'mastery': 418.2, 'masteryRating': 25380, 'offHandDmgMax': 40387.0, 'offHandDmgMin': 38875.0,
                      'offHandDps': 27425.393, 'offHandSpeed': 3.8, 'parry': 116.17902, 'parryRating': 16055,
                      'power': 1838164, 'rangedDmgMax': 60618.0, 'rangedDmgMin': 51016.0, 'rangedDps': 23017.041,
                      'rangedSpeed': 3.253, 'speedRating': 1089.0, 'speedRatingBonus': 18.596735,
                      'spellCrit': 134.29715, 'spellCritRating': 24400, 'spellPen': 0, 'sta': 82710, 'str': 36373,
                      'versatility': 12720, 'versatilityDamageDoneBonus': 49.86, 'versatilityDamageTakenBonus': 24.93,
                      'versatilityHealingDoneBonus': 49.86}
    stats_minimum_global = {'agi': 5, 'armor': 0, 'avoidanceRating': 0.0, 'avoidanceRatingBonus': 0.0, 'block': 0.0,
                      'blockRating': 0, 'crit': 0.0, 'critRating': 0, 'dodge': 0.0, 'dodgeRating': 0,
                      'haste': -27.033333, 'hasteRating': 0, 'hasteRatingPercent': 0.0, 'health': 306, 'int': 9,
                      'leech': -60.0, 'leechRating': -60.0, 'leechRatingBonus': 0.0, 'mainHandDmgMax': 1.0,
                      'mainHandDmgMin': 0.0, 'mainHandDps': 0.125, 'mainHandSpeed': 0.667, 'mana5': 0.0,
                      'mana5Combat': 0.0, 'mastery': 0.0, 'masteryRating': 0, 'offHandDmgMax': 0.0,
                      'offHandDmgMin': 0.0, 'offHandDps': 0.0, 'offHandSpeed': 0.667, 'parry': 0.0, 'parryRating': 0,
                      'power': 0, 'rangedDmgMax': -1.0, 'rangedDmgMin': -1.0, 'rangedDps': -1.0, 'rangedSpeed': -1.0,
                      'speedRating': -30.518183, 'speedRatingBonus': 0.0, 'spellCrit': 0.0017, 'spellCritRating': 0,
                      'spellPen': 0, 'sta': 17, 'str': 5, 'versatility': 0, 'versatilityDamageDoneBonus': 0.0,
                      'versatilityDamageTakenBonus': 0.0, 'versatilityHealingDoneBonus': 0.0}
    stats_mean_global = {'agi': 4672.277258699044, 'armor': 2001.4727582581563, 'avoidanceRating': 1.1033004669121393,
                   'avoidanceRatingBonus': 0.6885062033465073, 'block': 1.3070891963135096, 'blockRating': 0.0,
                   'crit': 19.73010125068563, 'critRating': 2254.2289264396663, 'dodge': 6.478166307476653,
                   'dodgeRating': 25.950705419521128, 'haste': 16.06888523653173, 'hasteRating': 2158.5366572271587,
                   'hasteRatingPercent': 13.908714036594885, 'health': 807942.6857703656, 'int': 7015.019343925931,
                   'leech': 0.26359496126975535, 'leechRating': 1.0811484874981898,
                   'leechRatingBonus': 0.2476907445228239, 'mainHandDmgMax': 10017.458861832734,
                   'mainHandDmgMin': 8765.198996981619, 'mainHandDps': 3855.6615863063903,
                   'mainHandSpeed': 2.2483025800377368, 'mana5': 9009.75571881571, 'mana5Combat': 8805.484450247575,
                   'mastery': 49.83102065901402, 'masteryRating': 2645.372286847996,
                   'offHandDmgMax': 3091.2397536118838, 'offHandDmgMin': 2875.3589754459745,
                   'offHandDps': 1586.8783813258156, 'offHandSpeed': 1.8170947186799526, 'parry': 4.011504966751173,
                   'parryRating': 114.33363714983382, 'power': 154321.02565200435, 'rangedDmgMax': 656.4463558977142,
                   'rangedDmgMin': 628.8855558570169, 'rangedDps': 240.6216909360749,
                   'rangedSpeed': -0.8339633597300509, 'speedRating': 28.23419487996765,
                   'speedRatingBonus': 0.5558401780802803, 'spellCrit': 20.06153050474746,
                   'spellCritRating': 2254.2282481516654, 'spellPen': 0.0, 'sta': 13278.711697924438,
                   'str': 3836.495574170793, 'versatility': 1540.4860611815777,
                   'versatilityDamageDoneBonus': 8.622942339860389, 'versatilityDamageTakenBonus': 4.311471171076854,
                   'versatilityHealingDoneBonus': 8.622942339860389}
    stats_max_dist_global = 5990271.526328605


if __name__ == "__main__":
    main()