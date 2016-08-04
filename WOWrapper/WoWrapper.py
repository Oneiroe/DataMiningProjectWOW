##### WoWrapper
# Functions to call transparently Blizzard API

import requests
import os
import json
import time
import logging
import sys

##### global variables
# API Credentials
credentials_file = open(os.path.join(os.path.dirname(__file__), 'APIcredential.csv'), 'r')
API_KEY = credentials_file.readline().split(',')[1][0:-1]  # key to query the APIs
API_SECRET_KEY = credentials_file.readline().split(',')[1][0:-1]  # key to perform query with sensible data
LIMIT_CALL_PER_SEC = int(credentials_file.readline().split(',')[1][
                         0:-1])  # call Rate Limits per second for a key. --100	Calls per second--
LIMIT_CALL_PER_HOUR = int(credentials_file.readline().split(',')[
                              1])  # call Rate Limits per hour for a key --36,000	Calls per hour--
credentials_file.close()

#
MAX_ATTEMPTS = 10  # Maximal number of attempts for an API call before giving up
CONNECTION_TIMEOUT = 3  # Timeout before raise a timeout exception (rises exponentially)
RETRY_TIMEOUT = 5  # Timeout before retry a request after receiving a 50x HTTP error
LAST_CALL_TIMESTAMP = 0  # last api call timestamp
MIN_TIME_LAPSE = 1 / (LIMIT_CALL_PER_HOUR / 3600)


##################
#### API CALL ####

# call the api at the requested link
def api_request(link):
    logging.debug('START API request')
    global CONNECTION_TIMEOUT
    global LAST_CALL_TIMESTAMP
    global RETRY_TIMEOUT

    # Check if between call is last enough time
    if (time.time() - LAST_CALL_TIMESTAMP) < MIN_TIME_LAPSE:
        time.sleep(1)
    LAST_CALL_TIMESTAMP = time.time()

    for attempt in range(MAX_ATTEMPTS):
        try:
            request = requests.get(link, timeout=CONNECTION_TIMEOUT)
            request.raise_for_status()  # Rise exception if response code different from 200
            response_json = request.json()
            logging.debug('END API request')
            return [request.status_code, response_json]

        # In the event of a network problem (e.g. DNS failure, refused connection, etc)
        except requests.exceptions.ConnectionError as err:
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            time.sleep(RETRY_TIMEOUT)  # in sec
            RETRY_TIMEOUT += RETRY_TIMEOUT
            if(RETRY_TIMEOUT>3600):
                RETRY_TIMEOUT=1200
            logging.warning('new retry time for requests:' + str(RETRY_TIMEOUT))
            continue

        # Triggered Timeout
        except requests.exceptions.Timeout as err:
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            time.sleep(5)  # in sec
            CONNECTION_TIMEOUT += CONNECTION_TIMEOUT
            logging.warning('new timeout for connections:' + str(CONNECTION_TIMEOUT))
            continue

        # Response code different from 200
        except requests.exceptions.HTTPError as err:
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            if request.status_code > 500:
                # Probable connection error, wait and retry
                time.sleep(RETRY_TIMEOUT)  # in sec
                RETRY_TIMEOUT += RETRY_TIMEOUT
                if(RETRY_TIMEOUT>3600):
                    RETRY_TIMEOUT=1200
                logging.warning('new retry time for requests:' + str(RETRY_TIMEOUT))
                continue
            else:
                logging.debug('END API request')
                return [request.status_code]

        # Unknown ambiguous request error
        except requests.exceptions.RequestException as err:
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            logging.debug('END API request')
            return [0]

        # Exception while decoding Json response
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            continue

        # Generic Exception while decoding Json response
        except ValueError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
            continue
    logging.debug('END API request')
    return [0]


###########################
#### WRAPPER FUNCTIONS ####
# the following function generate the request link for the API

#####################
#### ACHIEVEMENT ####

# This provides data about an individual achievement.
def get_achievement(nation, locale, achievement_id, key=API_KEY):
    logging.debug('get_achievement(' + nation + ', ' + locale + ', ' + achievement_id + '')
    link = "https://" + nation + ".api.battle.net/wow/achievement/" + achievement_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


#################
#### AUCTION ####

# Auction APIs currently provide rolling batches of data about current auctions.
# Fetching auction dumps is a two step process that involves
#   checking a per-realm index file to determine if a recent dump has been generated and
#   then fetching the most recently generated dump file if necessary.

# This API resource provides a per-realm list of recently generated auction house data dumps.
def get_auction(nation, locale, realm, key=API_KEY):
    logging.debug('get_auction(' + nation + ', ' + locale + ', ' + realm + ')')
    link = "https://" + nation + ".api.battle.net/wow/auction/data/" + realm + \
           "?locale=" + locale + \
           "&apikey=" + key
    auction = api_request(link)
    if auction[0] == 200:
        auction_json = auction[1]
        # Second phase
        return api_request(auction_json['files'][0]['url'])
    else:
        return [auction[0]]


##############
#### BOSS ####

# A list of all supported bosses. A 'boss' in this context should be considered a boss encounter,
# which may include more than one NPC.
def get_boss_masterlist(nation, locale, key=API_KEY):
    logging.debug('get_boss_masterlist(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/boss/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The boss API provides information about bosses. A 'boss' in this context should be considered a boss encounter,
# which may include more than one NPC.
def get_boss(nation, locale, boss_id, key=API_KEY):
    logging.debug('get_boss(' + nation + ', ' + locale + ', ' + boss_id + '')
    link = "https://" + nation + ".api.battle.net/wow/boss/" + boss_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###################
#### CHALLENGE ####

# The data in this request has data for all 9 challenge mode maps (currently).
# The map field includes the current medal times for each dungeon.
# Inside each ladder we provide data about each character that was part of each run.
# The character data includes the current cached spec of the character
# while the member field includes the spec of the character during the challenge mode run.
def get_realm_leaderboard(nation, locale, realm, key=API_KEY):
    logging.debug('get_realm_leaderboard(' + nation + ', ' + locale + ', ' + realm + ')')
    link = "https://" + nation + ".api.battle.net/wow/challenge/" + realm + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The region leaderboard has the exact same data format as the realm leaderboards except there is no realm field.
# It is simply the top 100 results gathered for each map for all of the available realm leaderboards in a region.
def get_region_leaderboard(nation, locale, key=API_KEY):
    logging.debug('get_region_leaderboard(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/challenge/region" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###################
#### CHARACTER ####

# The Character Profile API is the primary way to access character information.
# This Character Profile API can be used to fetch a single character at a time through an HTTP GET request
# to a URL describing the character profile resource.
# By default,a basic dataset will be returned and with each request and zero or more additional fields can be retrieved.
# To access this API, craft a resource URL pointing to the character who's information is to be retrieved.

# Retrieve character basic info
def get_character(nation, locale, realm, name, key=API_KEY):
    logging.debug('get_character(' + nation + ', ' + locale + ', ' + realm + ', ' + name + ')')
    link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# Retrieve character selected fields info
def get_character_selected_fileds(nation, locale, realm, name, fields, key=API_KEY):
    logging.debug(
        'get_character_selected_fileds(' + nation + ', ' + locale + ', ' + realm + ', ' + name + ', ' + fields + ')')
    link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + fields
    return api_request(link)


# Retrieve character full info at once
def get_character_full(nation, locale, realm, name, key=API_KEY):
    logging.debug('get_character_full(' + nation + ', ' + locale + ', ' + realm + ', ' + name + ')')
    link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + "achievements," \
                        "appearance," \
                        "feed," \
                        "guild," \
                        "hunterPets," \
                        "items," \
                        "mounts," \
                        "pets," \
                        "petSlots," \
                        "professions," \
                        "progression," \
                        "pvp," \
                        "quests," \
                        "reputation," \
                        "statistics," \
                        "stats," \
                        "talents," \
                        "titles," \
                        "audit"
    return api_request(link)


###############
#### GUILD ####

# The guild profile API is the primary way to access guild information.
# This guild profile API can be used to fetch a single guild at a time through an HTTP GET request to a url
# describing the guild profile resource.
# By default,a basic dataset will be returned and with each request and zero or more additional fields can be retrieved.

# There are no required query string parameters when accessing this resource,
# although the fields query string parameter can optionally be passed
# to indicate that one or more of the optional datasets is to be retrieved.
# Those additional fields are listed in the method titled "Optional Fields".

# Retrieve guild  basic info
def get_guild(nation, locale, realm, guild_name, key=API_KEY):
    logging.debug('get_guild(' + nation + ', ' + locale + ', ' + realm + ', ' + guild_name + ')')
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# Retrieve guild selected fields info
def get_guild_selected_fields(nation, locale, realm, guild_name, fields, key=API_KEY):
    logging.debug(
        'get_guild_selected_fields(' + nation + ', ' + locale + ', ' + realm + ', ' + guild_name + ', ' + fields + ')')
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + fields
    return api_request(link)


# Retrieve guild full info at once
def get_guild_full(nation, locale, realm, guild_name, key=API_KEY):
    logging.debug('get_guild_full(' + nation + ', ' + locale + ', ' + realm + ', ' + guild_name + ')')
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + "members," \
                        "achievements," \
                        "news," \
                        "challenge"
    return api_request(link)


##############
#### ITEM ####

# The item API provides detailed item information. This includes item set information if this item is part of a set.
def get_item(nation, locale, item_id, key=API_KEY):
    logging.debug('get_item(' + nation + ', ' + locale + ', ' + item_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/item/" + item_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# This provides item set information.
def get_item_set(nation, locale, set_id, key=API_KEY):
    logging.debug('get_item_set(' + nation + ', ' + locale + ', ' + set_id + '')
    link = "https://" + nation + ".api.battle.net/wow/item/set/" + set_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###############
#### MOUNT ####

# A list of all supported mounts.
def get_mount_masterlist(nation, locale, key=API_KEY):
    logging.debug('get_mount_masterlist(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/mount/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


#############
#### PET ####

# A list of all supported battle and vanity pets.
def get_pet_masterlist(nation, locale, key=API_KEY):
    logging.debug('get_pet_masterlist(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/pet/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# This provides data about a individual battle pet ability ID. We do not provide the tooltip for the ability yet.
# We are working on a better way to provide this since it depends on your pet's species, level and quality rolls.
def get_pet_ability(nation, locale, ability_id, key=API_KEY):
    logging.debug('get_pet_ability(' + nation + ', ' + locale + ', ' + ability_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/pet/ability/" + ability_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# This provides the data about an individual pet species.
# The species IDs can be found your character profile using the options pets field.
# Each species also has data about what it's 6 abilities are.
def get_pet_species(nation, locale, species_id, key=API_KEY):
    logging.debug('get_pet_species(' + nation + ', ' + locale + ', ' + species_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/pet/stat/" + species_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# Retrieve detailed information about a given species of pet.
def get_pet_species_stat(nation, locale, species_id, level, breed_id, quality_id, key=API_KEY):
    logging.debug(
        'get_pet_species_stat(' + nation + ', ' + locale + ', ' + species_id + ', ' + level + ', ' + breed_id + ', ' + quality_id + '')
    link = "https://" + nation + ".api.battle.net/wow/pet/stats/" + species_id + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&level=" + level + \
           "&breedId=" + breed_id + \
           "&qualityId=" + quality_id
    return api_request(link)


#############
#### PVP ####

# The Leaderboard API endpoint provides leaderboard information for the 2v2,3v3,5v5 and Rated Battleground leaderboards.
def get_pvp_leaderboard(nation, locale, bracket, key=API_KEY):
    logging.debug('get_pvp_leaderboard(' + nation + ', ' + locale + ', ' + bracket + ')')
    link = "https://" + nation + ".api.battle.net/wow/leaderboard/" + bracket + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###############
#### QUEST ####

# Retrieve metadata for a given quest.
def get_quest(nation, locale, quest_id, key=API_KEY):
    logging.debug('get_quest(' + nation + ', ' + locale + ', ' + quest_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/quest/" + quest_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###############
#### REALM ####

# The realm status API allows developers to retrieve realm status information.
# This information is limited to whether or not the realm is up, the type and state of the realm,
# the current population, and the status of the two world PvP zones.

# There are no required query string parameters when accessing this resource,
# although the optional realms parameter can be used to limit the realms returned to a specific set of realms.

def get_realm_status(nation, locale, key=API_KEY):
    logging.debug('get_real_status(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/realm/status" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


################
#### RECIPE ####

# The recipe API provides basic recipe information.
def get_recipe(nation, locale, recipe_id, key=API_KEY):
    logging.debug('get_recipe(' + nation + ', ' + locale + ', ' + recipe_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/recipe/" + recipe_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


###############
#### SPELL ####

# The spell API provides some information about spells.
def get_spell(nation, locale, spell_id, key=API_KEY):
    logging.debug('get_spell(' + nation + ', ' + locale + ', ' + spell_id + ')')
    link = "https://" + nation + ".api.battle.net/wow/spell/" + spell_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


##############
#### ZONE ####

# A list of all supported zones and their bosses.
# A 'zone' in this context should be considered a dungeon, or a raid, not a zone as in a world zone.
# A 'boss' in this context should be considered a boss encounter, which may include more than one NPC.
def get_zone_masterlist(nation, locale, key=API_KEY):
    logging.debug('get_zone_masterlist(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/zone/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The Zone API provides some information about zones.
def get_zone(nation, locale, zone_id, key=API_KEY):
    logging.debug('get_zone(' + nation + ', ' + locale + ', ' + zone_id + '')
    link = "https://" + nation + ".api.battle.net/wow/zone/" + zone_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


##############
#### DATA ####

# The battlegroups data API provides the list of battlegroups for this region. Please note the trailing / on this URL.
def get_data_battlegroups(nation, locale, key=API_KEY):
    logging.debug('get_data_battlegroups(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/battlegroups/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The character races data API provides a list of each race and their associated faction, name, unique ID, and skin.
def get_data_races(nation, locale, key=API_KEY):
    logging.debug('get_data_races(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/character/races" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The character classes data API provides a list of character classes.
def get_data_classes(nation, locale, key=API_KEY):
    logging.debug('get_data_classes(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/character/classes" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The character achievements data API provides a list of all of the achievements
# that characters can earn as well as the category structure and hierarchy.
def get_data_achievements(nation, locale, key=API_KEY):
    logging.debug('get_data_achievements(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/character/achievements" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The guild rewards data API provides a list of all guild rewards.
def get_data_guild_rewards(nation, locale, key=API_KEY):
    logging.debug('get_data_guild_rewards(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/guild/rewards" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The guild perks data API provides a list of all guild perks.
def get_data_guild_perks(nation, locale, key=API_KEY):
    logging.debug('get_data_guild_perks(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/guild/perks" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The guild achievements data API provides a list of all of the achievements
# that guilds can earn as well as the category structure and hierarchy.
def get_data_guild_achievements(nation, locale, key=API_KEY):
    logging.debug('get_data_guild_achievements(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/guild/achievements" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The item classes data API provides a list of item classes
def get_data_item_classes(nation, locale, key=API_KEY):
    logging.debug('get_data_item_classes(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/item/classes" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The talents data API provides a list of talents, specs and glyphs for each class.
def get_data_talents(nation, locale, key=API_KEY):
    logging.debug('get_data_talents(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/talents" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)


# The different bat pet types (including what they are strong and weak against)
def get_data_pet_types(nation, locale, key=API_KEY):
    logging.debug('get_data_pet_types(' + nation + ', ' + locale + ')')
    link = "https://" + nation + ".api.battle.net/wow/data/pet/types" + \
           "?locale=" + locale + \
           "&apikey=" + key
    return api_request(link)
