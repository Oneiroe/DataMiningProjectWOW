"""
WoWanalyzer
Retrieves relevant info and performs analysis over the downloaded data in DB
"""

import json
import os
import logging
import sys
import csv
from tqdm import tqdm
from collections import Counter
import time
import WOWanalysis.frequent_itemsets_apriori as my_apriori
import pickle
import numpy as np

###############################################
####
# LOG setup
logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'analyzer_DEBUG.log'),
                    level=logging.DEBUG,
                    format='%(asctime)-15s '
                           '%(levelname)s '
                           '--%(filename)s-- '
                           '%(message)s')

####
# GLOBAL VARIABLES

DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')

locations = {
    'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU'],
    'KR': ['ko_KR'],
    'TW': ['zh_TW'],
    'US': ['en_US', 'pt_BR', 'es_MX']
}

BRACKETS = ['2v2', '3v3', '5v5', 'rbg']

TRASH_PATH_SUFFIX = 'TRASH'

###############################################
# TO-DO
"""
Assignation: "I'd say that as a topic it's interesting.
I'd go with a, b, and something along e, which is not yet clear, but can lead to some interesting findings."

    a) Preliminary general simple statistical studies per server/nation (to acquire data and get confident with the API) like
            - number of players,
            - players characters_ranking,
            - most frequent character genre/sex/class,
            - distribution of character wrt their level,
            - most used characters,
            - average playtime wrt character level,
            - average time to level up,
            - guilds stats,
            ... and so on;

    b) Frequent itemset of players' equipment for every class in each nation.
    Then comparison between overall frequent itemset and per class frequent itemset, highlighting so items owned
    frequently by every player and ones just by specific classes;

    e) Study of character variance (or how much players are similar to each other?):
    it is expected that more you go through the game, more you personalize your character;
    is it actually true or in the end every player tends to converge to the same similar characters?
"""


#
###############################################

###############################################
# DATASET CLEANING
def clean_characters_dataset(region, locale):
    """ move to a special folder all the corrupted or empty json files for the given region"""
    logging.debug('clean_characters_dataset(' + region + ', ' + locale + ')')
    result_list = []
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    TRASH_PATH = os.path.join(CHARACTER_PATH, TRASH_PATH_SUFFIX)
    if not os.path.exists(TRASH_PATH):
        os.mkdir(TRASH_PATH)
    for file in os.listdir(CHARACTER_PATH):
        if not file.endswith('.json'):
            continue
        with open(os.path.join(CHARACTER_PATH, file)) as character_file:
            try:
                character_json = json.load(character_file)
                try:
                    if len(character_json.keys()) == 0:
                        result_list.append(str(os.path.join(CHARACTER_PATH, file)))
                        # character_json['achievementPoints']
                except KeyError as err:
                    logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    result_list.append(str(os.path.join(CHARACTER_PATH, file)))
            except json.decoder.JSONDecodeError as err:
                # logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                result_list.append(str(os.path.join(CHARACTER_PATH, file)))
                continue

    for file in result_list:
        if not os.path.exists(os.path.join(TRASH_PATH, os.path.basename(file))):
            os.rename(file, os.path.join(TRASH_PATH, os.path.basename(file)))

    return len(result_list)


def clean_json_dataset():
    """ move to a special folders all the corrupted or empty json files for the dataset"""
    logging.debug('clean_json_dataset()')
    tot_operations = 0

    for root, subFolders, files in os.walk(DB_BASE_PATH):
        logging.debug(root)
        if TRASH_PATH_SUFFIX in root:
            continue
        TRASH_PATH = os.path.join(root, TRASH_PATH_SUFFIX)
        for file in files:
            if not file.endswith('.json'):
                continue
            with open(os.path.join(root, file)) as open_file:
                try:
                    json_file = json.load(open_file)
                    try:
                        if len(json_file.keys()) == 0:
                            if not os.path.exists(TRASH_PATH):
                                os.mkdir(TRASH_PATH)
                            open_file.close()
                            if not os.path.exists(os.path.join(TRASH_PATH, file)):
                                os.rename(os.path.join(root, file), os.path.join(TRASH_PATH, file))
                            else:
                                os.remove(os.path.join(root, file))
                            tot_operations += 1

                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        if not os.path.exists(TRASH_PATH):
                            os.mkdir(TRASH_PATH)
                        open_file.close()
                        if not os.path.exists(os.path.join(TRASH_PATH, file)):
                            os.rename(os.path.join(root, file), os.path.join(TRASH_PATH, file))
                        else:
                            os.remove(os.path.join(root, file))
                        tot_operations += 1
                except json.decoder.JSONDecodeError as err:
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    if not os.path.exists(TRASH_PATH):
                        os.mkdir(TRASH_PATH)
                    open_file.close()
                    if not os.path.exists(os.path.join(TRASH_PATH, file)):
                        os.rename(os.path.join(root, file), os.path.join(TRASH_PATH, file))
                    else:
                        os.remove(os.path.join(root, file))
                    tot_operations += 1

    return tot_operations


# TODO
def clean_duplicates():
    """ Move to special folders duplicates entries, leaving the more useful (ie. containing more info) """
    pass


###############################################
# PRE-PROCESSING
def one_pass_characters_locale(region, locale, output_path):
    """ Retrieve all the information required with a single scan of the DB for the given locale.
    Build a DB in a single file with just the relevant info of all the characters"""
    logging.info('one_pass_locale(' + region + ', ' + locale + ')')
    # PATHs
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    number_players = len(os.listdir(CHARACTER_PATH))
    number_distinct_players = len(set(os.listdir(CHARACTER_PATH)))

    ACHIEVEMENTS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'achievements')
    # maps achievements id to their natural language name
    leveling_achievements_id_names = {}
    # Find all leveling achievements
    with open(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')) as achievements_file:
        try:
            achievements_json = json.load(achievements_file)
            try:
                # achievements_json['achievements'][0] -> id=92
                for i in achievements_json['achievements'][0]['achievements'][0:12]:
                    leveling_achievements_id_names[i['id']] = i['icon']
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))

    # Characters
    with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            ['name', 'realm', 'region', 'locale', 'class', 'level', 'race', 'gender', 'achievementPoints',
             'firstTimestamp', 'lastModified', 'TimestampLv10', 'TimestampLv20', 'TimestampLv30', 'TimestampLv40',
             'TimestampLv50', 'TimestampLv60', 'TimestampLv70', 'TimestampLv80', 'TimestampLv85', 'TimestampLv90',
             'TimestampLv100', 'TimestampLv110'])
        with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
            for file in os.listdir(CHARACTER_PATH):
                pbar.update(1)
                if not file.endswith('.json'):
                    continue
                with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                    try:
                        character_json = json.load(character_file)
                        try:
                            character_out = []
                            # 'name',
                            character_out.append(character_json['name'])
                            # 'realm',
                            character_out.append(character_json['realm'])
                            # 'region',
                            character_out.append(region)
                            # 'locale',
                            character_out.append(locale)
                            # 'class',
                            character_out.append(character_json['class'])
                            # 'level',
                            character_out.append(character_json['level'])
                            # 'race',
                            character_out.append(character_json['race'])
                            # 'gender',
                            character_out.append(character_json['gender'])
                            # 'achievementPoints',
                            character_out.append(character_json['achievementPoints'])
                            # 'firstTimestamp',
                            for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                                if i > 0:
                                    character_out.append(i)
                                    break
                            # 'lastModified',
                            character_out.append(character_json['lastModified'])

                            # 'TimestampLv10-110',
                            for achievement in leveling_achievements_id_names:
                                try:
                                    index = character_json['achievements']['achievementsCompleted'].index(achievement)
                                    # for low levels this difference can be 0
                                    character_out.append(
                                        character_json['achievements']['achievementsCompletedTimestamp'][index])
                                except ValueError:
                                    # achievement not completed
                                    character_out.append(None)
                                    continue

                            # Write character data into file
                            writer.writerow(character_out)
                        except KeyError as err:
                            logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                            logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    except json.decoder.JSONDecodeError as err:
                        # Probable incomplete or wrongly downloaded data, retry
                        logging.warning(
                            'JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                        continue
    return


def one_pass_characters(output_path, locations):
    """ Retrieve all the information required with a single scan of the whole DB.
        Build a csv DB in a single file with just the relevant info of all the characters.
        Serialize the characters map into a pickle object.
    """
    logging.info('one_pass_characters()')
    # TODO also port to sqLite DB

    # this will be serialized as pickle
    # key:region+'_'+locale+'_'+character file name, value map similar to the json
    map_output = {}
    pickle_output_path = os.path.join(output_path, 'serialized_character_map_global.pickle')

    items_fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}

    with open(os.path.join(output_path, 'CHARACTERS_DB_RELEVANT_GLOBAL.csv'),
              'w',
              newline='',
              encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(
            ['file', 'name', 'realm', 'region', 'locale', 'class', 'level', 'race', 'gender', 'achievementPoints',
             'firstTimestamp', 'lastModified', 'TimestampLv10', 'TimestampLv20', 'TimestampLv30',
             'TimestampLv40',
             'TimestampLv50', 'TimestampLv60', 'TimestampLv70', 'TimestampLv80', 'TimestampLv85',
             'TimestampLv90',
             'TimestampLv100', 'TimestampLv110'])
        for region in locations:
            for locale in locations[region]:
                logging.debug('one_pass_characters()...[' + region + ',' + locale + ']...')
                # PATHs
                DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
                CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

                locale_output_path = os.path.join(output_path,
                                                  'CHARACTERS_DB_RELEVANT_' + region + '_' + locale + '.csv')
                locale_output_file = open(locale_output_path, 'w', newline='', encoding='utf-8')
                locale_writer = csv.writer(locale_output_file)
                locale_writer.writerow(
                    ['file', 'name', 'realm', 'region', 'locale', 'class', 'level', 'race', 'gender',
                     'achievementPoints', 'firstTimestamp', 'lastModified', 'TimestampLv10', 'TimestampLv20',
                     'TimestampLv30', 'TimestampLv40', 'TimestampLv50', 'TimestampLv60', 'TimestampLv70',
                     'TimestampLv80', 'TimestampLv85', 'TimestampLv90', 'TimestampLv100', 'TimestampLv110'])

                ACHIEVEMENTS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'achievements')
                # maps achievements id to their natural language name
                leveling_achievements_id_names = {}
                # Find all leveling achievements
                with open(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')) as achievements_file:
                    try:
                        achievements_json = json.load(achievements_file)
                        try:
                            # achievements_json['achievements'][0] -> id=92
                            for i in achievements_json['achievements'][0]['achievements'][0:12]:
                                leveling_achievements_id_names[i['id']] = i['icon']
                        except KeyError as err:
                            logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                            logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))
                    except json.decoder.JSONDecodeError as err:
                        # Probable incomplete or wrongly downloaded data, retry
                        logging.warning(
                            'JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))

                # Characters
                with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
                    for file in os.listdir(CHARACTER_PATH):
                        pbar.update(1)
                        if not file.endswith('.json'):
                            continue
                        with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                            try:
                                character_json = json.load(character_file)
                                try:
                                    ########################################## CSV
                                    character_out = []
                                    # 'file',
                                    character_out.append(file)
                                    # 'name',
                                    character_out.append(character_json['name'])
                                    # 'realm',
                                    character_out.append(character_json['realm'])
                                    # 'region',
                                    character_out.append(region)
                                    # 'locale',
                                    character_out.append(locale)
                                    # 'class',
                                    character_out.append(character_json['class'])
                                    # 'level',
                                    character_out.append(character_json['level'])
                                    # 'race',
                                    character_out.append(character_json['race'])
                                    # 'gender',
                                    character_out.append(character_json['gender'])
                                    # 'achievementPoints',
                                    character_out.append(character_json['achievementPoints'])
                                    # 'firstTimestamp',
                                    for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                                        if i > 0:
                                            character_out.append(i)
                                            break
                                    # 'lastModified',
                                    character_out.append(character_json['lastModified'])

                                    # 'TimestampLv10-110',
                                    for achievement in leveling_achievements_id_names:
                                        try:
                                            index = character_json['achievements']['achievementsCompleted'].index(
                                                achievement)
                                            # for low levels this difference can be 0
                                            character_out.append(
                                                character_json['achievements']['achievementsCompletedTimestamp'][index])
                                        except ValueError:
                                            # achievement not completed
                                            character_out.append(None)
                                            continue

                                    # Write character data into file
                                    writer.writerow(character_out)
                                    locale_writer.writerow(character_out)

                                    ########################################## PICKLE
                                    # APPEARANCE
                                    character_appearance = list(character_json['appearance'].values())

                                    # ITEMS
                                    character_items = set()
                                    for field in character_json['items']:
                                        if field in items_fields_to_skip:
                                            continue
                                        character_items.add(character_json['items'][field]['id'])

                                    # MOUNTS
                                    character_mounts = set()
                                    for mount in character_json['mounts']['collected']:
                                        character_mounts.add(mount['creatureId'])

                                    # PETS
                                    character_pets = set()
                                    for pet in character_json['pets']['collected']:
                                        character_pets.add(pet['creatureId'])

                                    # PROFESSIONS
                                    character_professions = set()
                                    for primary_profession in character_json['professions']['primary']:
                                        character_professions.add(primary_profession['id'])
                                    for secondary_profession in character_json['professions']['secondary']:
                                        character_professions.add(secondary_profession['id'])

                                    # STATS (normalized)
                                    character_stats = character_json['stats']
                                    character_stats.pop('powerType')
                                    character_stats = list(character_stats.values())

                                    # TALENTS
                                    character_talents = set()
                                    for category in character_json['talents']:
                                        for talent in category['talents']:
                                            if talent is not None:
                                                character_talents.add(talent['spell']['id'])

                                    # write output
                                    map_output[region + '_' + locale + '_' + file] = {
                                        'appearance': character_appearance,
                                        'items': character_items,
                                        'mounts': character_mounts,
                                        'pets': character_pets,
                                        'professions': character_professions,
                                        'stats': character_stats,
                                        'talents': character_talents,
                                        'class': character_json['class'],
                                        'level': character_json['level'],
                                        'file': file,
                                        'locale': locale,
                                        'region': region
                                    }
                                except KeyError as err:
                                    logging.warning(
                                        'KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                                except ValueError as err:
                                    logging.warning(
                                        'ValueError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                            except json.decoder.JSONDecodeError as err:
                                # Probable incomplete or wrongly downloaded data, retry
                                logging.warning(
                                    'JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                                logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                                continue
                locale_output_file.close()

    logging.debug('one_pass_characters(): serializing to pickle')
    with open(pickle_output_path, 'wb') as f:
        pickle.dump(map_output, f, pickle.HIGHEST_PROTOCOL)
    return


def csv_unique(original_csv_path, output_path):
    """ Returns a csv DB without doubles"""
    # TODO
    return


def pickle_numpy_upgrade(original_pickle_path, output_path):
    """ Convert the numerical array of the serialized character map into numpy arrays """
    logging.info('pickle_numpy_upgrade()')
    with open(original_pickle_path, 'rb') as f:
        characters_map = pickle.load(f)
    with tqdm(total=len(characters_map)) as pbar:
        for character in characters_map:
            pbar.update(1)
            characters_map[character]['stats'] = np.array(characters_map[character]['stats'])
    with open(output_path, 'wb') as f:
        pickle.dump(characters_map, f, pickle.HIGHEST_PROTOCOL)
    return


def pickle_unique(original_pickle_path, output_path):
    """ Create a picke with only unique characters """
    logging.info('pickle_unique()')
    with open(original_pickle_path, 'rb') as f:
        original_characters_map = pickle.load(f)
    unique_map = {}
    with tqdm(total=len(original_characters_map)) as pbar:
        for character in original_characters_map:
            pbar.update(1)
            file_name = original_characters_map[character]['file']
            if file_name in unique_map:
                if sys.getsizeof(unique_map[file_name]) < sys.getsizeof(original_characters_map[character]):
                    unique_map[file_name] = original_characters_map[character]
            else:
                unique_map[file_name] = original_characters_map[character]

    with open(output_path, 'wb') as f:
        pickle.dump(unique_map, f, pickle.HIGHEST_PROTOCOL)
    return


def pickle_subsets(original_pickle_path, outputh_base_path, common_prefix):
    """ Makes smaller Pickle-DBs from the over all big one:
    per Region,Per Locale, per class, per level, per class-level-90-100-110 """
    logging.info('pickle_subsets()')
    with open(original_pickle_path, 'rb') as f:
        original_characters_map = pickle.load(f)
    logging.info('Pickle dataset Loaded')

    locations = {
        'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU'],
        'KR': ['ko_KR'],
        'TW': ['zh_TW'],
        'US': ['en_US', 'pt_BR', 'es_MX']
    }

    regions_map = {}
    locales_map = {}
    for region in locations:
        regions_map[region] = {}
        for locale in locations[region]:
            locales_map[locale] = {}

    classes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    classes_map = {}
    for c in classes:
        classes_map[c] = {}

    levels_map = {}
    for l in range(111):
        levels_map[l] = {}

    # Build maps
    with tqdm(total=len(original_characters_map)) as pbar:
        for character in original_characters_map:
            pbar.update(1)
            region = original_characters_map[character]['region']
            locale = original_characters_map[character]['locale']
            classe = original_characters_map[character]['class']
            level = original_characters_map[character]['level']

            regions_map[region][character] = original_characters_map[character]
            locales_map[locale][character] = original_characters_map[character]
            classes_map[classe][character] = original_characters_map[character]
            levels_map[level][character] = original_characters_map[character]

    ### Output

    # common_prefix='serialized_character_map_numpy_unique'

    print('serializing regions_map')
    for region in locations:
        pickle_output_path = os.path.join(outputh_base_path, common_prefix + '_' + region + '.pickle')
        with open(pickle_output_path, 'wb') as f:
            pickle.dump(regions_map[region], f, pickle.HIGHEST_PROTOCOL)

    print('serializing locales_map')
    for region in locations:
        for locale in locations[region]:
            pickle_output_path = os.path.join(outputh_base_path, common_prefix + '_' + locale + '.pickle')
            with open(pickle_output_path, 'wb') as f:
                pickle.dump(locales_map[locale], f, pickle.HIGHEST_PROTOCOL)

    print('serializing classes_map')
    for c in classes:
        pickle_output_path = os.path.join(outputh_base_path, common_prefix + '_c' + str(c) + '.pickle')
        with open(pickle_output_path, 'wb') as f:
            pickle.dump(classes_map[c], f, pickle.HIGHEST_PROTOCOL)

    print('serializing levels_map')
    for l in range(111):
        if len(levels_map[l]) > 0:
            pickle_output_path = os.path.join(outputh_base_path, common_prefix + '_lv' + str(l) + '.pickle')
            with open(pickle_output_path, 'wb') as f:
                pickle.dump(levels_map[l], f, pickle.HIGHEST_PROTOCOL)
    return


def pickle_combining(class_pickle, level_pickle, output_path):
    """ returns a pickle combining the common character of a certain level and class"""
    logging.info('pickle_combining()')
    with open(class_pickle, 'rb') as f:
        class_map = pickle.load(f)
    with open(level_pickle, 'rb') as f:
        level_map = pickle.load(f)
    intersection_map = {}
    intersection = set(class_map.keys()).intersection(set(level_map.keys()))
    for i in intersection:
        intersection_map[i] = class_map[i]

    with open(output_path, 'wb') as f:
        pickle.dump(intersection_map, f, pickle.HIGHEST_PROTOCOL)

    return


###############################################
# STATS
##############
# TODO separe functions in RETRIEVE/GENERATE and GET :
#   the former scan the DB and create a file with the interested data, the latter just scan that file
##############

def number_of_players_retrieved_total() -> int:
    """ Returns the number of players that have been retrieved from the API"""
    logging.debug('number_of_players_retrieved_total()')

    result = 0
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_distinct_players_retrieved_total() -> int:
    """ Returns the number of distinct players that have been retrieved from the API"""
    logging.debug('number_of_distinct_players_retrieved_total()')

    result_set = set()
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result_set.update(set(os.listdir(CHARACTER_PATH)))
    return len(result_set)


def number_of_players_retrieved_per_region() -> dict:
    """ Returns the number of player retrieved from each region from the API

    Returns:
        dict: key is the region, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_region()')

    result = {'EU': 0, 'KR': 0, 'TW': 0, 'US': 0}
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[region] += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_distinct_players_retrieved_per_region() -> dict:
    """ Returns the number of distinct players retrieved from each region from the API

    Returns:
        dict: key is the region, value the number of respective distinct players retrieved
    """
    logging.debug('number_of_distinct_players_retrieved_per_region()')

    result = {'EU': set(), 'KR': set(), 'TW': set(), 'US': set()}
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[region].update(set(os.listdir(CHARACTER_PATH)))
    for region in result:
        result[region] = len(result[region])
    return result


def number_of_players_retrieved_per_locale() -> dict:
    """ Returns the number of player retrieved from each locale from the API

    Returns:
        dict: key is the locale, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_locale()')

    result = {}
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[locale] = len(os.listdir(CHARACTER_PATH))
    return result


def number_of_distinct_players_retrieved_per_locale() -> dict:
    """ Returns the number of distinct player retrieved from each locale from the API

    Returns:
        dict: key is the locale, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_locale()')

    result = {}
    for region in locations:
        for locale in locations[region]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[locale] = set(os.listdir(CHARACTER_PATH))

    for locale in result:
        for other_locale in result:
            if other_locale != locale:
                result[locale].difference_update(result[other_locale])

    for locale in result:
        result[locale] = len(result[locale])

    return result


def players_locales_intersections(locales_iterator) -> set:
    """ Returns the set of player present in all the locales in input iterator"""
    logging.debug('players_locales_intersections(' + str(locales_iterator) + ')')

    # initialization with the first element of the iterator
    DB_CHARACTER_LOCALE_PATH = os.path.join(DB_BASE_PATH, locales_iterator[0][0], locales_iterator[0][1], 'character')
    player_set = set(os.listdir(DB_CHARACTER_LOCALE_PATH))
    intersection = player_set

    for region, locale in locales_iterator:
        DB_CHARACTER_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale, 'character')
        player_set = set(os.listdir(DB_CHARACTER_LOCALE_PATH))
        intersection.intersection_update(player_set)

    return intersection


def characters_ranking(region, locale, max_num=100):
    """ Return a list of max_num players from the given locale sorted by characters_ranking in decreasing order """
    logging.debug('characters_ranking(' + region + ', ' + locale + ', ' + str(max_num) + ')')

    leaderboard = [['', 0]]
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        if character_json['achievementPoints'] > leaderboard[-1][1] or len(leaderboard) < max_num:
                            # INSERTION SORT (linear)
                            i = 0
                            for character, score in leaderboard:
                                if character_json['achievementPoints'] > score:
                                    break
                                else:
                                    i += 1
                            leaderboard = \
                                leaderboard[0:i] + \
                                [(character_json['name'], character_json['achievementPoints'])] + \
                                leaderboard[i:100]
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    # print(leaderboard)
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'players_leaderboard_' + region + '_' + locale + '_TOP' + str(max_num) + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character, score in leaderboard:
            writer.writerow([character, score])

    return leaderboard


def gender_ranking(region, locale):
    """ Return the numbers of male and female characters for the given locale """
    logging.debug('gender_ranking(' + region + ', ' + locale + ')')

    result = Counter({1: 0, 0: 0})
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        result[character_json['gender']] += 1
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'gender_ranking_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for gender in result:
            writer.writerow([gender, result[gender]])

    return result


def race_ranking(region, locale):
    """ Return the numbers of characters per race for the given locale """
    logging.debug('race_ranking(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    RACES_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'races')

    result = Counter()
    # Find all races
    with open(os.path.join(RACES_PATH, 'races.json')) as races_file:
        try:
            races_json = json.load(races_file)
            try:
                for race in races_json['races']:
                    result[race['id']] = 0
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                logging.warning(str(os.path.join(RACES_PATH, 'races.json')))
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.warning(str(os.path.join(RACES_PATH, 'races.json')))

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        result[character_json['race']] += 1
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'race_ranking_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for race in result:
            writer.writerow([race, result[race]])

    return result


def class_ranking(region, locale):
    """ Return the numbers of characters per class for the given locale """
    logging.debug('class_ranking(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    CLASS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'classes')

    result = Counter()
    # Find all classes
    with open(os.path.join(CLASS_PATH, 'classes.json')) as classes_file:
        try:
            classes_json = json.load(classes_file)
            try:
                for character_class in classes_json['classes']:
                    result[character_class['id']] = 0
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        result[character_json['class']] += 1
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'class_ranking_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character_class in result:
            writer.writerow([character_class, result[character_class]])

    return result


def level_ranking(region, locale):
    """ Number pof players per level for the given locale """
    logging.debug('level_ranking(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    result = Counter()

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        character_level = character_json['level']
                        result[character_level] += 1
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)

    with open(os.path.join(os.getcwd(), 'Results',
                           'level_ranking_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for level, count in result.most_common():
            writer.writerow([level, count])

    return result


# MEMO WOW is out only from 2004
def avg_total_playtime(region, locale):
    """ Return the average total playtime(last timestamp-oldest achievement timestamp) for the given locale """
    # achievements > oldest(achievementsCompletedTimestamp)
    # time is in epoch (milliseconds)
    logging.debug('avg_total_playtime(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    result = 0
    num_players = 0

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                            if i > 0:
                                result += character_json['lastModified'] - i
                                num_players += 1
                                break
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print('total epoch: ' + str(result))
    print('total players: ' + str(num_players))
    result = result / num_players
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'avg_total_playtime_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        writer.writerow([result])

    return result


def playtime_characters_ranking(region, locale, max_num=100):
    """ Return a list of max_num players from the given locale
    sorted by characters total playtime in decreasing order """
    logging.debug('playtime_characters_ranking(' + region + ', ' + locale + ', ' + str(max_num) + ')')

    leaderboard = [['', 0]]
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        character_playtime = 0
                        for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                            if i > 0:
                                character_playtime = character_json['lastModified'] - i
                                break
                        if character_playtime > leaderboard[-1][1] or len(leaderboard) < max_num:
                            # INSERTION SORT (linear)
                            i = 0
                            for character, score in leaderboard:
                                if character_playtime > score:
                                    break
                                else:
                                    i += 1
                            leaderboard = \
                                leaderboard[0:i] + \
                                [(character_json['name'], character_playtime)] + \
                                leaderboard[i:100]
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    # print(leaderboard)
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'playtime_characters_ranking_' + region + '_' + locale + '_TOP' + str(max_num) + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character, character_playtime in leaderboard:
            writer.writerow([character, character_playtime])

    return leaderboard


# TODO adjust the results: biased by players restarting the game
def avg_playtime_per_level(region, locale):
    """ Return the avg total playtime for each character level for the given locale """
    logging.debug('avg_playtime_per_level(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    result = {}
    result_numers = {}

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        character_playtime = 0
                        for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                            if i > 0:
                                character_playtime = character_json['lastModified'] - i
                                break
                        result.setdefault(character_json['level'], 0)
                        result_numers.setdefault(character_json['level'], 0)
                        result[character_json['level']] += character_playtime
                        result_numers[character_json['level']] += 1
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)
    for i in result:
        result[i] = result[i] / result_numers[i]
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'avg_playtime_per_level_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for level_avg_playtime in result:
            writer.writerow([level_avg_playtime, result[level_avg_playtime]])

    return result


# TODO also here some player achieve levels "instantly", probably paying or starting again with a new character
def avg_leveling_playtime(region, locale):
    """ Return the avg time needed to reach a certain level for the given locale """
    logging.debug('avg_leveling_playtime(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    ACHIEVEMENTS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'achievements')

    result = {}
    result_numers = {}
    # maps achievements id to their natural language name
    id_names = {}

    # Find all leveling achievements
    with open(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')) as achievements_file:
        try:
            achievements_json = json.load(achievements_file)
            try:
                # achievements_json['achievements'][0] -> id=92
                for i in achievements_json['achievements'][0]['achievements'][0:12]:
                    id_names[i['id']] = i['icon']
                    result[i['id']] = 0
                    result_numers[i['id']] = 0
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.warning(str(os.path.join(ACHIEVEMENTS_PATH, 'achievements.json')))

    # Progressbar in terminal
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        character_start_playtime = 0
                        for i in sorted(character_json['achievements']['achievementsCompletedTimestamp']):
                            if i > 0:
                                character_start_playtime = i
                                break
                        for achievement in id_names:
                            try:
                                index = character_json['achievements']['achievementsCompleted'].index(achievement)
                                # for low levels this difference can be 0
                                result[achievement] += character_json['achievements']['achievementsCompletedTimestamp'][
                                                           index] - character_start_playtime
                                result_numers[achievement] += 1
                            except ValueError:
                                # achievement not completed
                                continue
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    print(result)
    for i in result:
        result[i] = result[i] / result_numers[i]
    # output to csv file
    with open(os.path.join(os.getcwd(), 'Results',
                           'avg_leveling_playtime_' + region + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for level_achievement in result:
            writer.writerow([id_names[level_achievement], level_achievement, result[level_achievement]])

    return result


###############################################
# FREQUENT ITEMSET
##############
# character field: "items"
# TODO
# next: mounts, pets, petSlots
# GRANULARITY per region, level
##############

def apriori_offline_frequent_itemsets_locale(region, locale, threshold):
    """ Returns the frequent itemset in invertory("items" character fields) of all the players for the given locale """
    logging.debug('apriori_offline_frequent_itemsets_locale(' + region + ', ' + locale + ')')

    # A-PRIORI
    input_file_path = os.path.join(os.getcwd(), 'Results', 'itemsets_' + region + '_' + locale + '.dat')
    output_file_path = os.path.join(os.getcwd(), 'Results', 'frequent_itemsets_' + region + '_' + locale + '.dat')
    input_file = open(input_file_path, "r")

    print('threshold:' + str(threshold))

    tstamp = time.time()
    print('#######################################')
    res_apriori = my_apriori.a_priori(input_file, output_file_path, threshold)
    freq_item_count = 0
    for i in res_apriori:
        freq_item_count += len(i)
    print('#######################################')
    print('Total frequent itemsets:' + str(freq_item_count))
    print('Total A-priori time:' + str(time.time() - tstamp))
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    input_file.close()
    return


def apriori_offline_frequent_itemsets_total(itemsets_path, output_path, threshold):
    """ Returns the frequent itemsets of the whole dataset """
    logging.debug('apriori_offline_frequent_itemsets_total()')

    # A-PRIORI
    input_file = open(itemsets_path, "r")

    print('threshold:' + str(threshold))

    tstamp = time.time()
    print('#######################################')
    res_apriori = my_apriori.a_priori(input_file, output_path, threshold)
    freq_item_count = 0
    for i in res_apriori:
        freq_item_count += len(i)
    print('#######################################')
    print('Total frequent itemsets:' + str(freq_item_count))
    print('Total A-priori time:' + str(time.time() - tstamp))
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    input_file.close()
    return


def apriori_offline_frequent_itemsets_level_locale(region, locale, threshold):
    """ Returns the frequent itemset in invertory("items" character fields)
    of all the players for the given locale grouped per level (10 lv per group)"""
    logging.debug('apriori_offline_frequent_itemsets_level_locale(' + region + ', ' + locale + ')')
    for level in range(0, 111, 10):
        # A-PRIORI
        input_file_path = os.path.join(os.getcwd(),
                                       'Results',
                                       'itemsets_' + region + '_' + locale + '_lv_' + str(level) + '.dat')
        output_file_path = os.path.join(os.getcwd(),
                                        'Results',
                                        'frequent_itemsets_' + region + '_' + locale + '_lv_' + str(level) + '.dat')
        input_file = open(input_file_path, "r")

        print('threshold:' + str(threshold))

        tstamp = time.time()
        print('#######################################')
        res_apriori = my_apriori.a_priori(input_file, output_file_path, threshold)
        freq_item_count = 0
        for i in res_apriori:
            freq_item_count += len(i)
        print('#######################################')
        print('Total frequent itemsets:' + str(freq_item_count))
        print('Total A-priori time:' + str(time.time() - tstamp))
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        input_file.close()
    return


def apriori_offline_frequent_itemsets_level_total(itemsets_base_path, output_base_path, threshold):
    """ Returns the frequent itemsets of the whole dataset per level"""
    logging.debug('apriori_offline_frequent_itemsets_level_total()')
    for level in range(0, 111, 10):
        # A-PRIORI

        input_file = open(os.path.join(itemsets_base_path, 'total_itemsets_lv_' + str(level) + '.dat'), 'r')
        output_path = os.path.join(output_base_path, 'total_frequent_itemsets_lv_' + str(level) + '.dat')
        print('threshold:' + str(threshold))

        tstamp = time.time()
        print('#######################################')
        res_apriori = my_apriori.a_priori(input_file, output_path, threshold)
        freq_item_count = 0
        for i in res_apriori:
            freq_item_count += len(i)
        print('#######################################')
        print('Total frequent itemsets:' + str(freq_item_count))
        print('Total A-priori time:' + str(time.time() - tstamp))
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        input_file.close()
    return


def apriori_offline_frequent_itemsets_class_level_locale(region, locale, threshold, classes):
    """ Returns the frequent itemset in invertory("items" character fields)
    of all the players for the given locale grouped per class and level (10 lv per group)"""
    logging.debug('apriori_offline_frequent_itemsets_class_level_locale(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CLASS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'classes')

    for character_class in classes:
        for level in range(0, 111, 10):
            # A-PRIORI
            input_file_path = os.path.join(os.getcwd(),
                                           'Results',
                                           'itemsets_' + region + '_' + locale + '_lv_' + str(level) + '_class_' + str(
                                               character_class) + '.dat')
            output_file_path = os.path.join(os.getcwd(),
                                            'Results',
                                            'frequent_itemsets_' + region + '_' + locale + '_lv_' + str(
                                                level) + '_class_' + str(character_class) + '.dat')
            input_file = open(input_file_path, "r")

            print('threshold:' + str(threshold))

            tstamp = time.time()
            print('#######################################')
            res_apriori = my_apriori.a_priori(input_file, output_file_path, threshold)
            freq_item_count = 0
            for i in res_apriori:
                freq_item_count += len(i)
            print('#######################################')
            print('Total frequent itemsets:' + str(freq_item_count))
            print('Total A-priori time:' + str(time.time() - tstamp))
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            input_file.close()
    return


def apriori_offline_frequent_itemsets_class_level_total(itemsets_base_path, output_base_path, threshold, classes):
    """ Returns the frequent itemsets of the whole dataset per class and level"""
    logging.debug('apriori_offline_frequent_itemsets_class_level_total()')

    for character_class in classes:
        for level in range(0, 111, 10):
            # A-PRIORI
            input_file = open(os.path.join(itemsets_base_path, 'total_itemsets_lv_' + str(level) + '_class_' + str(
                character_class) + '.dat'), 'r')
            output_path = os.path.join(output_base_path, 'total_frequent_itemsets_lv_' + str(level) + '_class_' + str(
                character_class) + '[threshold_' + str(threshold) + '].dat')
            print('threshold:' + str(threshold))

            tstamp = time.time()
            print('#######################################')
            res_apriori = my_apriori.a_priori(input_file, output_path, threshold)
            freq_item_count = 0
            for i in res_apriori:
                freq_item_count += len(i)
            print('#######################################')
            print('Total frequent itemsets:' + str(freq_item_count))
            print('Total A-priori time:' + str(time.time() - tstamp))
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            input_file.close()
    return


###############################################
logging.info('START analyzer')


def main():
    ### PRE-PROCESSING
    print('===PRE-PROCESSING')
    # Removed all corrupted json files
    # print('corrupted json files: ' + str(clean_json_dataset()))
    # Removed corrupted characters json files
    # print('files moved : ' + str(clean_characters_dataset('EU', 'it_IT')))
    # one_pass_characters_locale('EU', 'it_IT', 'ita_DB_test.csv')
    # one_pass_characters(os.path.join('Results', 'DBs', 'New'), locations)
    # pickle_numpy_upgrade(os.path.join('Results', 'DBs', 'serialized_character_map_global.pickle'),
    #                      os.path.join('Results', 'DBs', 'serialized_character_map_numpy_global.pickle'))
    # pickle_unique(os.path.join('Results', 'DBs', 'serialized_character_map_numpy_global.pickle'),
    #               os.path.join('Results', 'DBs', 'serialized_character_map_numpy_global_unique.pickle'))
    # pickle_subsets(os.path.join('Results', 'DBs', 'serialized_character_map_numpy_global_unique.pickle'),
    #                os.path.join('Results', 'DBs'),
    #                'serialized_character_map_numpy_unique')
    for c in range(1, 13):
        print(str(c))
        pickle_combining(os.path.join('Results', 'DBs', 'serialized_character_map_numpy_unique_c' + str(c) + '.pickle'),
                         os.path.join('Results', 'DBs', 'serialized_character_map_numpy_unique_lv100.pickle'),
                         os.path.join('Results', 'DBs','serialized_character_map_numpy_unique_c' + str(c) + '_lv100.pickle'))
    #### SIMPLE ANALYTICAL STUFF
    print('===SIMPLE ANALYSIS')

    # print('total #players:' + str(number_of_players_retrieved_total()))
    # print('distinct total #players:' + str(number_of_distinct_players_retrieved_total()))
    # print(number_of_players_retrieved_per_region())
    # print(number_of_distinct_players_retrieved_per_region())
    # print(number_of_players_retrieved_per_locale())
    # print(number_of_distinct_players_retrieved_per_locale())
    #
    # print(len(players_locales_intersections([('TW', 'zh_TW'), ('KR', 'ko_KR')])))
    # print(len(players_locales_intersections([('TW', 'zh_TW'), ('US', 'en_US')])))
    # print(len(players_locales_intersections([('TW', 'zh_TW'), ('EU', 'en_GB')])))
    #
    # print(len(players_locales_intersections([('KR', 'ko_KR'), ('US', 'en_US')])))
    # print(len(players_locales_intersections([('KR', 'ko_KR'), ('EU', 'en_GB')])))
    # print(len(players_locales_intersections([('US', 'en_US'), ('EU', 'en_GB')])))
    # print(len(players_locales_intersections([('EU', 'en_GB'), ('EU', 'de_DE'), ('EU', 'es_ES'), ('EU', 'fr_FR'),
    #                                          ('EU', 'it_IT'), ('EU', 'pt_PT'), ('EU', 'ru_RU')])))

    # print(characters_ranking('EU', 'it_IT', 100))
    # print(gender_ranking('EU', 'it_IT'))
    # print(race_ranking('EU', 'it_IT'))
    # print(class_ranking('EU', 'it_IT'))
    # print(avg_total_playtime('EU', 'it_IT'))
    # print(playtime_characters_ranking('EU', 'it_IT', 100))
    # print(avg_playtime_per_level('EU', 'it_IT'))
    # print(avg_leveling_playtime('EU', 'it_IT'))

    # print(level_ranking('EU', 'it_IT'))
    # for region in locations:
    #     for locale in locations[region]:
    #         level_ranking(region, locale)

    #### FREQUENT ITEMSET
    print('===FREQUENT ITEMSET')
    # ### APRIORI GENERAL
    # # for region in locations:
    # #     for locale in locations[region]:
    # #         output_path = 'itemsets_' + region + '_' + locale + '.dat'
    # #         my_apriori.create_locale_characters_itemsets(region, locale, DB_BASE_PATH, output_path)
    # # my_apriori.join_locales_characters_itemets(os.path.join(os.getcwd(), 'Results'),
    # #                                            os.path.join(os.getcwd(), 'Results', 'total_itemsets.dat'))
    # # apriori_offline_frequent_itemsets_locale('EU', 'it_IT', 0.01)
    # thresholds = [1, 0.75, 0.5, 0.25, 0.15, 0.1, 0.05, 0.01, 0.005, 0.002, 0.001]
    # for threshold in thresholds:
    #     threshold = 1
    #     # threshold = 0.05
    #     apriori_offline_frequent_itemsets_total(
    #         os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'total_itemsets.dat'),
    #         os.path.join(os.getcwd(), 'Results', 'frequent_itemsets', 'tests',
    #                      'total_frequent_itemsets[threshold_' + str(threshold) + '].dat'),
    #         threshold
    #     )
    #
    #     ### APRIORI per LEVEL
    #     # for region in locations:
    #     #     for locale in locations[region]:
    #     #         my_apriori.create_level_locale_characters_itemsets(region,
    #     #                                                            locale,
    #     #                                                            DB_BASE_PATH,
    #     #                                                            os.path.join(os.getcwd(), 'Results'))
    #     # my_apriori.join_level_locale_characters_itemets(os.path.join(os.getcwd(), 'Results'),
    #     #                                                  os.path.join(os.getcwd(), 'Results'))
    #     # for region in locations:
    #     #     for locale in locations[region]:
    #     #         apriori_offline_frequent_itemsets_level_locale(region, locale, 0.01)
    #     # apriori_offline_frequent_itemsets_level_total(os.path.join(os.getcwd(), 'Results'),
    #     #                                               os.path.join(os.getcwd(), 'Results'),
    #     #                                               0.01)
    #     #
    #
    #     ### APRIORI per CLASS and LEVEL
    #     # CLASS_PATH = os.path.join(DB_BASE_PATH, 'US', 'en_US', 'data', 'character', 'classes')
    #
    #     # classes = []
    #     # # Find all classes
    #     # with open(os.path.join(CLASS_PATH, 'classes.json')) as classes_file:
    #     #     try:
    #     #         classes_json = json.load(classes_file)
    #     #         try:
    #     #             for character_class in classes_json['classes']:
    #     #                 classes.append(character_class['id'])
    #     #         except KeyError as err:
    #     #             logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    #     #             logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))
    #     #     except json.decoder.JSONDecodeError as err:
    #     #         # Probable incomplete or wrongly downloaded data, retry
    #     #         logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    #     #         logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))
    #
    #     classes = [11]
    #     # threshold = 1
    #     # for region in locations:
    #     #     for locale in locations[region]:
    #     #         my_apriori.create_class_level_locale_characters_itemsets(region,
    #     #                                                                  locale,
    #     #                                                                  DB_BASE_PATH,
    #     #                                                                  os.path.join(os.getcwd(), 'Results'))
    #     # my_apriori.join_class_level_locale_characters_itemets(os.path.join(os.getcwd(), 'Results'),
    #     #                                                        os.path.join(os.getcwd(), 'Results'),
    #     #                                                        classes)
    #     # for region in locations:
    #     #     for locale in locations[region]:
    #     #         apriori_offline_frequent_itemsets_class_level_locale(region, locale, 0.01, classes)
    #     apriori_offline_frequent_itemsets_class_level_total(os.path.join(os.getcwd(), 'Results', 'frequent_itemsets'),
    #                                                         os.path.join(os.getcwd(), 'Results', 'frequent_itemsets',
    #                                                                      'tests'),
    #                                                         threshold,
    #                                                         classes)

    #### SIMILARITY
    print('===SIMILARITY')


if __name__ == "__main__":
    main()
