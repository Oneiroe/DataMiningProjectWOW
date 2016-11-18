##### WoWspider
# For each API call (functions of WoWrapper), extracts from the responses the info needed to retrieve other data


import json
import os
import logging
import sys

####
# LOG setup
# logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'INFO.log'),
#                     level=logging.INFO,
#                     format='%(asctime)-15s '
#                            '%(levelname)s '
#                            '--%(filename)s-- '
#                            '%(message)s')

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

###############################################
# TO-DO

#
###############################################

logging.info('START analyzer')


def number_of_players_retrieved_total() -> int:
    """ Returns the number of player that have been retrieved from the API"""
    logging.debug('number_of_players_retrieved_total()')

    result = 0
    for nation in location:
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            if not os.path.exists(DB_LOCALE_PATH):
                os.mkdir(DB_LOCALE_PATH)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            if not os.path.exists(CHARACTER_PATH):
                os.mkdir(CHARACTER_PATH)
            result += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_players_retrieved_per_nation() -> dict:
    """ Returns the number of player retrieved from each nation from the API

    Returns:
        dict: key is the nation, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_nation()')

    result = {'EU': 0, 'KR': 0, 'TW': 0, 'US': 0}
    for nation in location:
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            if not os.path.exists(DB_LOCALE_PATH):
                os.mkdir(DB_LOCALE_PATH)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            if not os.path.exists(CHARACTER_PATH):
                os.mkdir(CHARACTER_PATH)
            result[nation] += len(os.listdir(CHARACTER_PATH))
    return result


def number_of_players_retrieved_per_locale() -> dict:
    """ Returns the number of player retrieved from each locale from the API

    Returns:
        dict: key is the locale, value the number of respective players retrieved
    """
    logging.debug('number_of_players_retrieved_per_locale()')

    result = {}
    for nation in location:
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)
        for locale in location[nation]:
            DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
            if not os.path.exists(DB_LOCALE_PATH):
                os.mkdir(DB_LOCALE_PATH)
            CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
            if not os.path.exists(CHARACTER_PATH):
                os.mkdir(CHARACTER_PATH)
            result[locale] = len(os.listdir(CHARACTER_PATH))
    return result
