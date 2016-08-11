##### WoWcrawler
# it crawls through Blizzard API and saves the data as Json locally

import json
import WOWrapper.WoWrapper as WoWrapper
import WOWrapper.WoWspider as WoWspider
import os
import logging
import sys

####
# LOG setup
logging.basicConfig(filename=os.path.join(os.getcwd(), 'LOG', 'INFO.log'),
                    level=logging.INFO,
                    format='%(asctime)-15s '
                           '%(levelname)s '
                           '--%(filename)s-- '
                           '%(message)s')

####
# GLOBAL VARIABLES

DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')

location = {
    # 'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pl_PL', 'pt_PT', 'ru_RU'],
    'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU'],
    'KR': ['ko_KR'],
    'TW': ['zh_TW'],
    'US': ['en_US', 'pt_BR', 'es_MX']
}  # static map with available servers and relative nations
# continent: EU, KR, TW, US

BRACKETS = ['2v2', '3v3', '5v5', 'rbg']

###############################################
# TO-DO

# TODO add a "ALREADY DONE" SET to take note of already done without storing them
# TODO Updatable file or save some file with timestamp
# TODO download again if file corrupted
###############################################

logging.info('START crawler')

###############################################
# DATA RETRIEVABLE WITHOUT PREVIOUS KNOWLEDGE #

logging.info('CRAWLING Lv.0')
# DATA LISTS
for nation in location:
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
    if not os.path.exists(DB_LOCALE_PATH):
        os.mkdir(DB_LOCALE_PATH)
    for locale in location[nation]:
        # print(nation + ' ' + locale)
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)
        DATA_PATH = os.path.join(DB_LOCALE_PATH, 'data')
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)

        # Battlegroups
        try:
            PATH = os.path.join(DATA_PATH, 'battlegroups')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'battlegroups.json')):
                item = WoWrapper.get_data_battlegroups(nation, locale)
                if item[0] == 200:
                    file = open(os.path.join(PATH, 'battlegroups.json'), 'w')
                    json.dump(item[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(item[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            pass

        # character (super group)
        DATA_CHARACTER_PATH = os.path.join(DATA_PATH, 'character')
        if not os.path.exists(DATA_CHARACTER_PATH):
            os.mkdir(DATA_CHARACTER_PATH)
        # Races
        try:
            PATH = os.path.join(DATA_CHARACTER_PATH, 'races')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'races.json')):
                races = WoWrapper.get_data_races(nation, locale)
                if races[0] == 200:
                    file = open(os.path.join(PATH, 'races.json'), 'w')
                    json.dump(races[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(races[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            pass
        # Classes
        try:
            PATH = os.path.join(DATA_CHARACTER_PATH, 'classes')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'classes.json')):
                classes = WoWrapper.get_data_classes(nation, locale)
                if classes[0] == 200:
                    file = open(os.path.join(PATH, 'classes.json'), 'w')
                    json.dump(classes[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(classes[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        # Achievements
        try:
            PATH = os.path.join(DATA_CHARACTER_PATH, 'achievements')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'achievements.json')):
                achievements = WoWrapper.get_data_achievements(nation, locale)
                if achievements[0] == 200:
                    file = open(os.path.join(PATH, 'achievements.json'), 'w')
                    json.dump(achievements[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(achievements[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # guild (super group)
        DATA_GUILD_PATH = os.path.join(DATA_PATH, 'guild')
        if not os.path.exists(DATA_GUILD_PATH):
            os.mkdir(DATA_GUILD_PATH)
        # Rewards
        try:
            PATH = os.path.join(DATA_GUILD_PATH, 'rewards')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'rewards.json')):
                rewards = WoWrapper.get_data_guild_rewards(nation, locale)
                if rewards[0] == 200:
                    file = open(os.path.join(PATH, 'rewards.json'), 'w')
                    json.dump(rewards[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(rewards[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        # Perks
        try:
            PATH = os.path.join(DATA_GUILD_PATH, 'perks')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'perks.json')):
                perks = WoWrapper.get_data_guild_perks(nation, locale)
                if perks[0] == 200:
                    file = open(os.path.join(PATH, 'perks.json'), 'w')
                    json.dump(perks[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(perks[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        # Achievements
        try:
            PATH = os.path.join(DATA_GUILD_PATH, 'achievements')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'achievements.json')):
                achievements = WoWrapper.get_data_guild_achievements(nation, locale)
                if achievements[0] == 200:
                    file = open(os.path.join(PATH, 'achievements.json'), 'w')
                    json.dump(achievements[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(achievements[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Item
        try:
            PATH = os.path.join(DATA_PATH, 'item')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'item_classes.json')):
                item_classes = WoWrapper.get_data_item_classes(nation, locale)
                if item_classes[0] == 200:
                    file = open(os.path.join(PATH, 'item_classes.json'), 'w')
                    json.dump(item_classes[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(item_classes[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Talents
        try:
            PATH = os.path.join(DATA_PATH, 'talents')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'talents.json')):
                talents = WoWrapper.get_data_talents(nation, locale)
                if talents[0] == 200:
                    file = open(os.path.join(PATH, 'talents.json'), 'w')
                    json.dump(talents[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(talents[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Pet types
        try:
            PATH = os.path.join(DATA_PATH, 'pet')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'pet_types.json')):
                pet_types = WoWrapper.get_data_pet_types(nation, locale)
                if pet_types[0] == 200:
                    file = open(os.path.join(PATH, 'pet_types.json'), 'w')
                    json.dump(pet_types[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(pet_types[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

# DIRECT MASTERLISTS
for nation in location:
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
    if not os.path.exists(DB_LOCALE_PATH):
        os.mkdir(DB_LOCALE_PATH)
    for locale in location[nation]:
        # print(nation + ' ' + locale)
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)

        # Boss masterlist
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'boss')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'boss_masterlist.json')):
                boss_masterlist = WoWrapper.get_boss_masterlist(nation, locale)
                if boss_masterlist[0] == 200:
                    file = open(os.path.join(PATH, 'boss_masterlist.json'), 'w')
                    json.dump(boss_masterlist[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(boss_masterlist[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Mount masterlist
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'mount')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'mount_masterlist.json')):
                mount_masterlist = WoWrapper.get_mount_masterlist(nation, locale)
                if mount_masterlist[0] == 200:
                    file = open(os.path.join(PATH, 'mount_masterlist.json'), 'w')
                    json.dump(mount_masterlist[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(mount_masterlist[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Pet masterlist
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'pet')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'pet_masterlist.json')):
                pet_masterlist = WoWrapper.get_pet_masterlist(nation, locale)
                if pet_masterlist[0] == 200:
                    file = open(os.path.join(PATH, 'pet_masterlist.json'), 'w')
                    json.dump(pet_masterlist[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(pet_masterlist[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Realm status (aka ALL realms and their status)
        # updatable
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'realm')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            PATH = os.path.join(PATH, 'status')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'realm_status.json')):
                realm_status = WoWrapper.get_realm_status(nation, locale)
                if realm_status[0] == 200:
                    file = open(os.path.join(PATH, 'realm_status.json'), 'w')
                    json.dump(realm_status[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(realm_status[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Zone masterlist
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'zone')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'zone_masterlist.json')):
                zone_masterlist = WoWrapper.get_zone_masterlist(nation, locale)
                if zone_masterlist[0] == 200:
                    file = open(os.path.join(PATH, 'zone_masterlist.json'), 'w')
                    json.dump(zone_masterlist[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(zone_masterlist[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # Challenge region leaderboard
        # updatable
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'challenge')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            if not os.path.exists(os.path.join(PATH, 'region_leaderboard.json')):
                region_leaderboard = WoWrapper.get_region_leaderboard(nation, locale)
                if region_leaderboard[0] == 200:
                    file = open(os.path.join(PATH, 'region_leaderboard.json'), 'w')
                    json.dump(region_leaderboard[1], file, sort_keys=True, indent=4)
                    file.close()
                else:
                    # print(region_leaderboard[0])
                    pass
            else:
                # print("already exists")
                pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

        # PVP leaderboard
        # updatable
        try:
            PATH = os.path.join(DB_LOCALE_PATH, 'pvp')
            if not os.path.exists(PATH):
                os.mkdir(PATH)
            for bracket in BRACKETS:
                if not os.path.exists(os.path.join(PATH, bracket + '.json')):
                    pvp_leaderboard = WoWrapper.get_pvp_leaderboard(nation, locale, bracket)
                    if pvp_leaderboard[0] == 200:
                        file = open(os.path.join(PATH, bracket + '.json'), 'w')
                        json.dump(pvp_leaderboard[1], file, sort_keys=True, indent=4)
                        file.close()
                    else:
                        # print(pvp_leaderboard[0])
                        pass
                else:
                    # print("already exists")
                    pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))

############################################################
# 1° LEVEL DATA: DEPENDANT OF ONE PREVIOUSLY RETRIEVE INFO #
logging.info('CRAWLING cycle')
while True:
    try:
        ####################################
        ### SPIDER (analyze downloaded data)
        logging.info('START SPIDER: Scanning retrieved Json')

        # QUEUES : retrieved key waiting to be used to download the data from the API
        queue = {'item_id': set(),
                 'item_set_id': set(),
                 'realm': set(),
                 'character': set(),  # CSV character_name, realm
                 'character_name': set(),
                 'guild': set(),  # CSV guild_name, realm
                 'guild_name': set(),
                 'boss_id': set(),
                 'quest_id': set(),
                 'recipe_id': set(),
                 'spell_id': set(),
                 'zone_id': set(),
                 'pet_ability_id': set(),
                 'species_id': set(),
                 'achievement_id': set()
                 }

        # SEARCH : Open a downloaded Json and search for keys
        # for each item in each folder of DB
        try:
            for dirname, dirnames, filenames in os.walk(DB_BASE_PATH):
                logging.info('SEARCHING IN: ' + dirname)
                for filename in filenames:
                    logging.debug(os.path.join(dirname, filename))
                    try:
                        if filename.endswith('.json'):
                            file_path = os.path.join(dirname, filename)
                            # Choose the right function to analyze the file and
                            # put retrieved keys in QUEUE
                            if dirname.endswith(os.path.join('data', 'battlegroups')):
                                res = WoWspider.search_in_data_battlegroups(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'character', 'achievements')):
                                res = WoWspider.search_in_data_achievements(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'character', 'classes')):
                                res = WoWspider.search_in_data_classes(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'character', 'races')):
                                res = WoWspider.search_in_data_races(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'guild', 'achievements')):
                                res = WoWspider.search_in_data_guild_achievements(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'guild', 'perks')):
                                res = WoWspider.search_in_data_guild_perks(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'guild', 'rewards')):
                                res = WoWspider.search_in_data_guild_rewards(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'item')):
                                res = WoWspider.search_in_data_item_classes(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'pet')):
                                res = WoWspider.search_in_data_pet_types(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('data', 'talents')):
                                res = WoWspider.search_in_data_talents(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('achievement')):
                                res = WoWspider.search_in_achievement(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('auction')):
                                res = WoWspider.search_in_auction(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('boss')):
                                if filename == 'boss_masterlist':
                                    res = WoWspider.search_in_boss_masterlist(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                                else:
                                    res = WoWspider.search_in_boss(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                            elif dirname.endswith(os.path.join('challenge')):
                                if filename == 'region_leaderboard':
                                    res = WoWspider.search_in_region_leaderboard(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                                else:
                                    res = WoWspider.search_in_realm_leaderboard(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                            elif dirname.endswith(os.path.join('character')):
                                res = WoWspider.search_in_character_full(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('guild')):
                                res = WoWspider.search_in_guild_full(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('item')):
                                res = WoWspider.search_in_item(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('item', 'set')):
                                res = WoWspider.search_in_item_set(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('mount')):
                                res = WoWspider.search_in_mount_masterlist(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('pet')):
                                res = WoWspider.search_in_pet_masterlist(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('pet', 'ability')):
                                res = WoWspider.search_in_item(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('pet', 'species')):
                                res = WoWspider.search_in_item(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('pet', 'stat')):
                                res = WoWspider.search_in_item(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('pvp')):
                                res = WoWspider.search_in_pvp_leaderboard(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('quest')):
                                res = WoWspider.search_in_quest(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('realm', 'status')):
                                res = WoWspider.search_in_realm_status(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('recipe')):
                                res = WoWspider.search_in_recipe(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('spell')):
                                res = WoWspider.search_in_spell(file_path)
                                for key in res.keys():
                                    try:
                                        queue[key] = queue[key].union(res[key])
                                    except KeyError:
                                        pass
                            elif dirname.endswith(os.path.join('zone')):
                                if filename == 'zone_masterlist':
                                    res = WoWspider.search_in_zone_masterlist(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                                else:
                                    res = WoWspider.search_in_zone(file_path)
                                    for key in res.keys():
                                        try:
                                            queue[key] = queue[key].union(res[key])
                                        except KeyError:
                                            pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.exception(sys.last_traceback.tb_lineno)
                        pass
        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.exception(sys.last_traceback.tb_lineno)
            pass

        logging.info('END SPIDER')
        ##############################
        ### DOWNLOADER (retrieve data)
        logging.info('START DOWNLOADER: retrieving new data from queued keys')

        # TILL QUEUES EMPTY (after Lv.0)
        # EXECUTE IF element not already downloaded
        try:
            for nation in location:
                DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
                if not os.path.exists(DB_LOCALE_PATH):
                    os.mkdir(DB_LOCALE_PATH)
                for locale in location[nation]:
                    # print(nation + ' ' + locale)
                    logging.info('DOWNLOADING FROM: ' + nation + '-' + locale)
                    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
                    if not os.path.exists(DB_LOCALE_PATH):
                        os.mkdir(DB_LOCALE_PATH)
                    DATA_PATH = os.path.join(DB_LOCALE_PATH, 'data')
                    if not os.path.exists(DATA_PATH):
                        os.mkdir(DATA_PATH)

                    try:
                        # ITEMS
                        logging.debug('DOWNLOADER: ITEMS')
                        PATH = os.path.join(DB_LOCALE_PATH, 'item')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for item_id in queue['item_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(item_id) + '.json')):
                                item = WoWrapper.get_item(nation, locale, str(item_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(item_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # ITEM SETS
                        logging.debug('DOWNLOADER: ITEM SETS')
                        PATH = os.path.join(DB_LOCALE_PATH, 'item', 'set')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for item_set_id in queue['item_set_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(item_set_id) + '.json')):
                                item = WoWrapper.get_item_set(nation, locale, str(item_set_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(item_set_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # CHARACTER
                        logging.debug('DOWNLOADER: CHARACTER')
                        PATH = os.path.join(DB_LOCALE_PATH, 'character')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for character in queue['character']:
                            try:
                                # Check if already downloaded
                                character_name, realm = character.split(',')
                                if not os.path.exists(
                                        os.path.join(PATH, str(character_name) + '[' + str(realm) + ']' + '.json')):
                                    item = WoWrapper.get_character_full(nation, locale, str(realm), str(character_name))
                                    if item[0] == 200:
                                        file = open(
                                            os.path.join(PATH, str(character_name) + '[' + str(realm) + ']' + '.json'),
                                            'w')
                                        json.dump(item[1], file, sort_keys=True, indent=4)
                                        file.close()
                                    else:
                                        # print(item[0])
                                        pass
                                else:
                                    # print("already exists")
                                    pass
                            except IndexError as err:
                                logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # GUILD
                        logging.debug('DOWNLOADER: GUILD')
                        PATH = os.path.join(DB_LOCALE_PATH, 'guild')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for guild in queue['guild']:
                            try:
                                # Check if already downloaded
                                guild_name, realm = guild.split(',')
                                if not os.path.exists(
                                        os.path.join(PATH, str(guild_name) + '[' + str(realm) + ']' + '.json')):
                                    item = WoWrapper.get_guild_full(nation, locale, str(realm), str(guild_name))
                                    if item[0] == 200:
                                        file = open(
                                            os.path.join(PATH, str(guild_name) + '[' + str(realm) + ']' + '.json'), 'w')
                                        json.dump(item[1], file, sort_keys=True, indent=4)
                                        file.close()
                                    else:
                                        # print(item[0])
                                        pass
                                else:
                                    # print("already exists")
                                    pass
                            except IndexError as err:
                                logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # BOSS
                        logging.debug('DOWNLOADER: BOSS')
                        PATH = os.path.join(DB_LOCALE_PATH, 'boss')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for boss_id in queue['boss_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(boss_id) + '.json')):
                                item = WoWrapper.get_boss(nation, locale, str(boss_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(boss_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # QUEST
                        logging.debug('DOWNLOADER: QUSET')
                        PATH = os.path.join(DB_LOCALE_PATH, 'quest')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for quest_id in queue['quest_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(quest_id) + '.json')):
                                item = WoWrapper.get_quest(nation, locale, str(quest_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(quest_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # RECIPE
                        logging.debug('DOWNLOADER: RECIPE')
                        PATH = os.path.join(DB_LOCALE_PATH, 'recipe')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for recipe_id in queue['recipe_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(recipe_id) + '.json')):
                                item = WoWrapper.get_recipe(nation, locale, str(recipe_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(recipe_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # SPELL
                        logging.debug('DOWNLOADER: SPELL')
                        PATH = os.path.join(DB_LOCALE_PATH, 'spell')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for spell_id in queue['spell_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(spell_id) + '.json')):
                                item = WoWrapper.get_spell(nation, locale, str(spell_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(spell_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # ZONE
                        logging.debug('DOWNLOADER: ZONE')
                        PATH = os.path.join(DB_LOCALE_PATH, 'zone')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for zone_id in queue['zone_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(zone_id) + '.json')):
                                item = WoWrapper.get_zone(nation, locale, str(zone_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(zone_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # PET ABILITY
                        logging.debug('DOWNLOADER: PET ABILITY')
                        PATH = os.path.join(DB_LOCALE_PATH, 'pet', 'ability')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for ability_id in queue['pet_ability_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(ability_id) + '.json')):
                                item = WoWrapper.get_pet_ability(nation, locale, str(ability_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(ability_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # PET SPECIES
                        logging.debug('DOWNLOADER: PET SPECIES')
                        PATH = os.path.join(DB_LOCALE_PATH, 'pet', 'species')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for species_id in queue['species_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(species_id) + '.json')):
                                item = WoWrapper.get_pet_species(nation, locale, str(species_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(species_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

                    try:
                        # ACHIEVEMENT
                        logging.debug('DOWNLOADER: ACHIEVEMENT')
                        PATH = os.path.join(DB_LOCALE_PATH, 'achievement')
                        if not os.path.exists(PATH):
                            os.mkdir(PATH)
                        for achievement_id in queue['achievement_id']:
                            # Check if already downloaded
                            if not os.path.exists(os.path.join(PATH, str(achievement_id) + '.json')):
                                item = WoWrapper.get_achievement(nation, locale, str(achievement_id))
                                if item[0] == 200:
                                    file = open(os.path.join(PATH, str(achievement_id) + '.json'), 'w')
                                    json.dump(item[1], file, sort_keys=True, indent=4)
                                    file.close()
                                else:
                                    # print(item[0])
                                    pass
                            else:
                                # print("already exists")
                                pass
                    except KeyError:
                        pass
                    except os.error as err:
                        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        pass

        except os.error as err:
            logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            pass

        logging.info('END DOWNLOADER')

    except Exception as err:  # Just to be sure that it will run forever
        logging.warning(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
        pass
