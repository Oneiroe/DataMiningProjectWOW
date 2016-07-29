##### WoWcrawler
# it crawls through Blizzard API and saves the data as Json locally

import json
import WOWrapper.WoWrapper as WoWrapper
import os

DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')

location = {
    # 'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pl_PL', 'pt_PT', 'ru_RU'],
    'EU': ['en_GB', 'de_DE', 'es_ES', 'fr_FR', 'it_IT', 'pt_PT', 'ru_RU'],
    'KR': ['ko_KR'],
    'TW': ['zh_TW'],
    'US': ['en_US', 'pt_BR', 'es_MX']
}  # static map with available servers and relative nations
# continent: EU, KR, TW, US

# TODO: wrong error code management
# TODO: CALL limit awareness
# TODO: Logging

###############################################
# DATA RETRIEVABLE WITHOUT PREVIOUS KNOWLEDGE #

# DATA LIST
for nation in location:
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
    if not os.path.exists(DB_LOCALE_PATH):
        os.mkdir(DB_LOCALE_PATH)
    for locale in location[nation]:
        print(nation + ' ' + locale)
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)
        DATA_PATH = os.path.join(DB_LOCALE_PATH, 'data')
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)

        # Battlegroups
        PATH = os.path.join(DATA_PATH, 'battlegroups')
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        if not os.path.exists(os.path.join(PATH, 'battlegroups.json')):
            battlegroups = WoWrapper.get_data_battlegroups(nation, locale)
            if battlegroups[0] == 200:
                file = open(os.path.join(PATH, 'battlegroups.json'), 'w')
                json.dump(battlegroups[1], file, sort_keys=True, indent=4)
                file.close()
            else:
                print(battlegroups[0])
        else:
            print("already exists")

        # character (super group)
        DATA_CHARACTER_PATH = os.path.join(DATA_PATH, 'character')
        if not os.path.exists(DATA_CHARACTER_PATH):
            os.mkdir(DATA_CHARACTER_PATH)
        # Races
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
                print(races[0])
        else:
            print("already exists")
        # Classes
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
                print(classes[0])
        else:
            print("already exists")
        # Achievements
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
                print(achievements[0])
        else:
            print("already exists")

        # guild (super group)
        DATA_GUILD_PATH = os.path.join(DATA_PATH, 'guild')
        if not os.path.exists(DATA_GUILD_PATH):
            os.mkdir(DATA_GUILD_PATH)
        # Rewards
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
                print(rewards[0])
        else:
            print("already exists")
        # Perks
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
                print(perks[0])
        else:
            print("already exists")
        # Achievements
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
                print(achievements[0])
        else:
            print("already exists")

        # Item
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
                print(item_classes[0])
        else:
            print("already exists")

        # Talents
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
                print(talents[0])
        else:
            print("already exists")

        # Pet types
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
                print(pet_types[0])
        else:
            print("already exists")


# DIRECT MASTERLISTS
for nation in location:
    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation)
    if not os.path.exists(DB_LOCALE_PATH):
        os.mkdir(DB_LOCALE_PATH)
    for locale in location[nation]:
        print(nation + ' ' + locale)
        DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, nation, locale)
        if not os.path.exists(DB_LOCALE_PATH):
            os.mkdir(DB_LOCALE_PATH)

        # Boss masterlist
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
                print(boss_masterlist[0])
        else:
            print("already exists")

        # Mount masterlist
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
                print(mount_masterlist[0])
        else:
            print("already exists")

        # Pet masterlist
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
                print(pet_masterlist[0])
        else:
            print("already exists")

        # Realm status (aka ALL realms and their status)
        PATH = os.path.join(DB_LOCALE_PATH, 'realm')
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        if not os.path.exists(os.path.join(PATH, 'realm_status.json')):
            realm_status = WoWrapper.get_real_status(nation, locale)
            if realm_status[0] == 200:
                file = open(os.path.join(PATH, 'realm_status.json'), 'w')
                json.dump(realm_status[1], file, sort_keys=True, indent=4)
                file.close()
            else:
                print(realm_status[0])
        else:
            print("already exists")

        # Zone masterlist
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
                print(zone_masterlist[0])
        else:
            print("already exists")

        # TODO: Challenge region leaderboard
        # TODO: PVP leaderboard

############################################################
# 1° LEVEL DATA: DEPENDANT OF ONE PREVIOUSLY RETRIEVE INFO #
