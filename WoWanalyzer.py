##### WoWanalyzer
# Retrieves relevant info and performs analysis over the downloaded data in DB


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
"""
Assignation: "I'd say that as a topic it's interesting.
I'd go with a, b, and something along e, which is not yet clear, but can lead to some interesting findings."

    a) Preliminary general simple statistical studies per server/nation (to acquire data and get confident with the API) like
            - number of players,
            - players ranking,
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

logging.info('START analyzer')


def number_of_players_retrieved_total() -> int:
    """ Returns the number of players that have been retrieved from the API"""
    logging.debug('number_of_players_retrieved_total()')

    result = 0
    for nation in location:
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
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
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
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


def players_locale_intersections(nation_1: str, locale_1: str, nation_2: str, locale_2: str) -> set:
    """ Returns the number of player present in both the input locales"""
    logging.debug('players_locale_intersections(' + locale_1 + ',' + locale_2 + ')')

    DB_CHARACTER_LOCALE_1_PATH = os.path.join(DB_BASE_PATH, nation_1, locale_1, 'character')
    player_set_1 = set(os.listdir(DB_CHARACTER_LOCALE_1_PATH))

    DB_CHARACTER_LOCALE_2_PATH = os.path.join(DB_BASE_PATH, nation_2, locale_2, 'character')
    player_set_2 = set(os.listdir(DB_CHARACTER_LOCALE_2_PATH))

    return player_set_1.intersection(player_set_2)

print(number_of_distinct_players_retrieved_total())
print(number_of_players_retrieved_per_nation())