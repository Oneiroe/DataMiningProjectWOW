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

location = {
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
def clean_characters_dataset(nation, locale):
    """ move to a special folder all the corrupted or empty json files for the given nation"""
    logging.debug('clean_characters_dataset(' + nation + ', ' + locale + ')')
    result_list = []
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
# STATS
##############
# TODO separe functions in RETRIEVE/GENERATE and GET :
#   the former scan the DB and create a file with the interested data, the latter just scan that file
##############

def one_pass_locale(nation, locale):
    """ Retrieve all the information required with a single scan of the DB for the given locale"""
    logging.info('one_pass_locale(' + nation + ', ' + locale + ')')
    result = {
        'number_players': 0,
        'number_distinct_players': 0,
        'characters_ranking': []
    }
    # PATHs
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')

    # immediate
    result['number_players'] = len(os.listdir(CHARACTER_PATH))
    result['number_distinct_players'] = len(set(os.listdir(CHARACTER_PATH)))

    ### SCANS
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
                        # INFO RETRIEVAL HERE
                        # RANKING


                        pass
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue

    return result


def number_of_players_retrieved_total() -> int:
    """ Returns the number of players that have been retrieved from the API"""
    logging.debug('number_of_players_retrieved_total()')

    result = 0
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_distinct_players_retrieved_total() -> int:
    """ Returns the number of distinct players that have been retrieved from the API"""
    logging.debug('number_of_distinct_players_retrieved_total()')

    result_set = set()
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result_set.update(set(os.listdir(CHARACTER_PATH)))
    return len(result_set)


def number_of_players_retrieved_per_nation() -> dict:
    """ Returns the number of player retrieved from each nation from the API

    Returns:
        dict: key is the nation, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_nation()')

    result = {'EU': 0, 'KR': 0, 'TW': 0, 'US': 0}
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[nation] += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_distinct_players_retrieved_per_nation() -> dict:
    """ Returns the number of distinct players retrieved from each nation from the API

    Returns:
        dict: key is the nation, value the number of respective distinct players retrieved
    """
    logging.debug('number_of_distinct_players_retrieved_per_nation()')

    result = {'EU': set(), 'KR': set(), 'TW': set(), 'US': set()}
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            result[nation].update(set(os.listdir(CHARACTER_PATH)))
    for nation in result:
        result[nation] = len(result[nation])
    return result


def number_of_players_retrieved_per_locale() -> dict:
    """ Returns the number of player retrieved from each locale from the API

    Returns:
        dict: key is the locale, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_locale()')

    result = {}
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
    for nation in location:
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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

    for nation, locale in locales_iterator:
        DB_CHARACTER_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale, 'character')
        player_set = set(os.listdir(DB_CHARACTER_LOCALE_PATH))
        intersection.intersection_update(player_set)

    return intersection


def characters_ranking(nation, locale, max_num=100):
    """ Return a list of max_num players from the given locale sorted by characters_ranking in decreasing order """
    logging.debug('characters_ranking(' + nation + ', ' + locale + ', ' + str(max_num) + ')')

    leaderboard = [['', 0]]
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'players_leaderboard_' + nation + '_' + locale + '_TOP' + str(max_num) + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character, score in leaderboard:
            writer.writerow([character, score])

    return leaderboard


def gender_ranking(nation, locale):
    """ Return the numbers of male and female characters for the given locale """
    logging.debug('gender_ranking(' + nation + ', ' + locale + ')')

    result = Counter({1: 0, 0: 0})
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'gender_ranking_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for gender in result:
            writer.writerow([gender, result[gender]])

    return result


def race_ranking(nation, locale):
    """ Return the numbers of characters per race for the given locale """
    logging.debug('race_ranking(' + nation + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'race_ranking_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for race in result:
            writer.writerow([race, result[race]])

    return result


def class_ranking(nation, locale):
    """ Return the numbers of characters per class for the given locale """
    logging.debug('class_ranking(' + nation + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'class_ranking_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character_class in result:
            writer.writerow([character_class, result[character_class]])

    return result


# MEMO WOW is out only from 2004
def avg_total_playtime(nation, locale):
    """ Return the average total playtime(last timestamp-oldest achievement timestamp) for the given locale """
    # achievements > oldest(achievementsCompletedTimestamp)
    # time is in epoch (milliseconds)
    logging.debug('avg_total_playtime(' + nation + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'avg_total_playtime_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        writer.writerow([result])

    return result


def playtime_characters_ranking(nation, locale, max_num=100):
    """ Return a list of max_num players from the given locale
    sorted by characters total playtime in decreasing order """
    logging.debug('playtime_characters_ranking(' + nation + ', ' + locale + ', ' + str(max_num) + ')')

    leaderboard = [['', 0]]
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'playtime_characters_ranking_' + nation + '_' + locale + '_TOP' + str(max_num) + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for character, character_playtime in leaderboard:
            writer.writerow([character, character_playtime])

    return leaderboard


# TODO adjust the results: biased by players restarting the game
def avg_playtime_per_level(nation, locale):
    """ Return the avg total playtime for each character level for the given locale """
    logging.debug('avg_playtime_per_level(' + nation + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'avg_playtime_per_level_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for level_avg_playtime in result:
            writer.writerow([level_avg_playtime, result[level_avg_playtime]])

    return result


# TODO also here some player achieve levels "instantly", probably paying or starting again with a new character
def avg_leveling_playtime(nation, locale):
    """ Return the avg time needed to reach a certain level for the given locale """
    logging.debug('avg_leveling_playtime(' + nation + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
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
                           'avg_leveling_playtime_' + nation + '_' + locale + '.csv'),
              'w',
              newline='',
              encoding='utf-8') as output:
        writer = csv.writer(output)
        for level_achievement in result:
            writer.writerow([id_names[level_achievement], level_achievement, result[level_achievement]])

    return result


###############################################
logging.info('START analyzer')


def main():
    ### PRE-PROCESSING
    print('===PRE-PROCESSING')
    # Removed all corrupted json files
    # print('corrupted json files: ' + str(clean_json_dataset()))
    # Removed corrupted characters json files
    # print('files moved : ' + str(clean_characters_dataset('EU', 'it_IT')))

    #### SIMPLE ANALYTICAL STUFF
    print('===SIMPLE ANALYSIS')

    print('total #players:' + str(number_of_players_retrieved_total()))
    print('distinct total #players:' + str(number_of_distinct_players_retrieved_total()))
    print(number_of_players_retrieved_per_nation())
    print(number_of_distinct_players_retrieved_per_nation())
    print(number_of_players_retrieved_per_locale())
    print(number_of_distinct_players_retrieved_per_locale())

    print(len(players_locales_intersections([('TW', 'zh_TW'), ('KR', 'ko_KR')])))
    print(len(players_locales_intersections([('TW', 'zh_TW'), ('US', 'en_US')])))
    print(len(players_locales_intersections([('TW', 'zh_TW'), ('EU', 'en_GB')])))

    print(len(players_locales_intersections([('KR', 'ko_KR'), ('US', 'en_US')])))
    print(len(players_locales_intersections([('KR', 'ko_KR'), ('EU', 'en_GB')])))
    print(len(players_locales_intersections([('US', 'en_US'), ('EU', 'en_GB')])))
    print(len(players_locales_intersections([('EU', 'en_GB'), ('EU', 'de_DE'), ('EU', 'es_ES'), ('EU', 'fr_FR'),
                                             ('EU', 'it_IT'), ('EU', 'pt_PT'), ('EU', 'ru_RU')])))

    # print(characters_ranking('EU', 'it_IT', 100))
    # print(gender_ranking('EU', 'it_IT'))
    # print(race_ranking('EU', 'it_IT'))
    # print(class_ranking('EU', 'it_IT'))
    # print(avg_total_playtime('EU', 'it_IT'))
    # print(playtime_characters_ranking('EU', 'it_IT', 100))
    # print(avg_playtime_per_level('EU', 'it_IT'))
    # print(avg_leveling_playtime('EU', 'it_IT'))


if __name__ == "__main__":
    main()
