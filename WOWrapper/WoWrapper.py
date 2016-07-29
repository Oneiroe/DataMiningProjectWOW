##### WoWrapper
# Functions to call transparently Blizzard API

import requests
import os

##### global variables
# API Credentials
credentials_file = open(os.path.join(os.path.dirname(__file__),'APIcredential.csv'), 'r')
API_KEY = credentials_file.readline().split(',')[1][0:-1]  # key to query the APIs
API_SECRET_KEY = credentials_file.readline().split(',')[1][0:-1]  # key to perform query with sensible data
LIMIT_CALL_PER_SEC = credentials_file.readline().split(',')[1][
                     0:-1]  # call Rate Limits per second for a key. --100	Calls per second--
LIMIT_CALL_PER_HOUR = credentials_file.readline().split(',')[
    1]  # call Rate Limits per hour for a key --36,000	Calls per hour--
credentials_file.close()

###########################
#### WRAPPER FUNCTIONS ####


#####################
#### ACHIEVEMENT ####

# This provides data about an individual achievement.
def get_achievement(nation, locale, achievement_id, key=API_KEY):
    achievement_link = "https://" + nation + ".api.battle.net/wow/achievement/" + achievement_id + \
                       "?locale=" + locale + \
                       "&apikey=" + key
    achievement = requests.get(achievement_link)
    if achievement.status_code == 200:
        achievement_json = achievement.json()
        return [achievement.status_code, achievement_json]
    else:
        return [achievement.status_code]


#################
#### AUCTION ####

# Auction APIs currently provide rolling batches of data about current auctions.
# Fetching auction dumps is a two step process that involves
#   checking a per-realm index file to determine if a recent dump has been generated and
#   then fetching the most recently generated dump file if necessary.

# This API resource provides a per-realm list of recently generated auction house data dumps.
def get_auction(nation, locale, realm, key=API_KEY):
    auction_link = "https://" + nation + ".api.battle.net/wow/auction/data/" + realm + \
                   "?locale=" + locale + \
                   "&apikey=" + key
    auction = requests.get(auction_link)
    if auction.status_code == 200:
        auction_json = auction.json()
        # Second phase
        auction_json = requests.get(auction_json['files'][0]['url']).json()
        return [auction.status_code, auction_json]
    else:
        return [auction.status_code]


##############
#### BOSS ####

# A list of all supported bosses. A 'boss' in this context should be considered a boss encounter,
# which may include more than one NPC.
def get_boss_masterlist(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/boss/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The boss API provides information about bosses. A 'boss' in this context should be considered a boss encounter,
# which may include more than one NPC.
def get_boss(nation, locale, boss_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/boss/" + boss_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###################
#### CHALLENGE ####

# The data in this request has data for all 9 challenge mode maps (currently).
# The map field includes the current medal times for each dungeon.
# Inside each ladder we provide data about each character that was part of each run.
# The character data includes the current cached spec of the character
# while the member field includes the spec of the character during the challenge mode run.
def get_realm_leaderboard(nation, locale, realm, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/challenge/" + realm + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The region leaderboard has the exact same data format as the realm leaderboards except there is no realm field.
# It is simply the top 100 results gathered for each map for all of the available realm leaderboards in a region.
def get_region_leaderboard(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/challenge/region" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###################
#### CHARACTER ####

# The Character Profile API is the primary way to access character information.
# This Character Profile API can be used to fetch a single character at a time through an HTTP GET request
# to a URL describing the character profile resource.
# By default,a basic dataset will be returned and with each request and zero or more additional fields can be retrieved.
# To access this API, craft a resource URL pointing to the character who's information is to be retrieved.

# Retrieve character basic info
def get_character(nation, locale, realm, name, key=API_KEY):
    character_link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
                     "?locale=" + locale + \
                     "&apikey=" + key
    character = requests.get(character_link)
    if character.status_code == 200:
        character_json = character.json()
        return [character.status_code, character_json]
    else:
        return [character.status_code]


# Retrieve character selected fields info
def get_character_selected_fileds(nation, locale, realm, name, fields, key=API_KEY):
    character_link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
                     "?locale=" + locale + \
                     "&apikey=" + key + \
                     "&fields=" + fields
    character = requests.get(character_link)
    if character.status_code == 200:
        character_json = character.json()
        return [character.status_code, character_json]
    else:
        return [character.status_code]


# Retrieve character full info at once
def get_character_full(nation, locale, realm, name, key=API_KEY):
    character_link = "https://" + nation + ".api.battle.net/wow/character/" + realm + "/" + name + \
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
    character = requests.get(character_link)
    if character.status_code == 200:
        character_json = character.json()
        return [character.status_code, character_json]
    else:
        return [character.status_code]


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
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# Retrieve guild selected fields info
def get_guild_selected_fields(nation, locale, realm, guild_name, fields, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + fields
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# Retrieve guild full info at once
def get_guild_full(nation, locale, realm, guild_name, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/guild/" + realm + "/" + guild_name + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&fields=" + "members," \
                        "achievements," \
                        "news," \
                        "challenge"
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


##############
#### ITEM ####

# The item API provides detailed item information. This includes item set information if this item is part of a set.
def get_item(nation, locale, item_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/item/" + item_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# This provides item set information.
def get_item_set(nation, locale, set_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/item/set/" + set_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###############
#### MOUNT ####

# A list of all supported mounts.
def get_mount_masterlist(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/mount/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


#############
#### PET ####

# A list of all supported battle and vanity pets.
def get_pet_masterlist(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/pet/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# This provides data about a individual battle pet ability ID. We do not provide the tooltip for the ability yet.
# We are working on a better way to provide this since it depends on your pet's species, level and quality rolls.
def get_pet_ability(nation, locale, ability_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/pet/ability/" + ability_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# This provides the data about an individual pet species.
# The species IDs can be found your character profile using the options pets field.
# Each species also has data about what it's 6 abilities are.
def get_pet_species(nation, locale, species_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/pet/stat/" + species_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# Retrieve detailed information about a given species of pet.
def get_pet_species_stat(nation, locale, species_id, level, breed_id, quality_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/pet/stats/" + species_id + \
           "?locale=" + locale + \
           "&apikey=" + key + \
           "&level=" + level + \
           "&breedId=" + breed_id + \
           "&qualityId=" + quality_id
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


##############
#### PVP ####

# The Leaderboard API endpoint provides leaderboard information for the 2v2,3v3,5v5 and Rated Battleground leaderboards.
def get_pvp_leaderboard(nation, locale, bracket, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/leaderboard/" + bracket + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###############
#### QUEST ####

# Retrieve metadata for a given quest.
def get_quest(nation, locale, quest_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/quest/" + quest_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###############
#### REALM ####

# The realm status API allows developers to retrieve realm status information.
# This information is limited to whether or not the realm is up, the type and state of the realm,
# the current population, and the status of the two world PvP zones.

# There are no required query string parameters when accessing this resource,
# although the optional realms parameter can be used to limit the realms returned to a specific set of realms.

def get_real_status(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/realm/status" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


################
#### RECIPE ####

# The recipe API provides basic recipe information.
def get_recipe(nation, locale, recipe_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/recipe/" + recipe_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


###############
#### SPELL ####

# The spell API provides some information about spells.
def get_spell(nation, locale, spell_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/spell/" + spell_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


##############
#### ZONE ####

# A list of all supported zones and their bosses.
# A 'zone' in this context should be considered a dungeon, or a raid, not a zone as in a world zone.
# A 'boss' in this context should be considered a boss encounter, which may include more than one NPC.
def get_zone_masterlist(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/zone/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The Zone API provides some information about zones.
def get_zone(nation, locale, zone_id, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/zone/" + zone_id + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


##############
#### DATA ####

# The battlegroups data API provides the list of battlegroups for this region. Please note the trailing / on this URL.
def get_data_battlegroups(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/battlegroups/" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The character races data API provides a list of each race and their associated faction, name, unique ID, and skin.
def get_data_races(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/character/races" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The character classes data API provides a list of character classes.
def get_data_classes(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/character/classes" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The character achievements data API provides a list of all of the achievements
# that characters can earn as well as the category structure and hierarchy.
def get_data_achievements(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/character/achievements" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The guild rewards data API provides a list of all guild rewards.
def get_data_guild_rewards(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/guild/rewards" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The guild perks data API provides a list of all guild perks.
def get_data_guild_perks(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/guild/perks" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The guild achievements data API provides a list of all of the achievements
# that guilds can earn as well as the category structure and hierarchy.
def get_data_guild_achievements(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/guild/achievements" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The item classes data API provides a list of item classes
def get_data_item_classes(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/item/classes" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The talents data API provides a list of talents, specs and glyphs for each class.
def get_data_talents(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/talents" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]


# The different bat pet types (including what they are strong and weak against)
def get_data_pet_types(nation, locale, key=API_KEY):
    link = "https://" + nation + ".api.battle.net/wow/data/pet/types" + \
           "?locale=" + locale + \
           "&apikey=" + key
    request = requests.get(link)
    if request.status_code == 200:
        response_json = request.json()
        return [request.status_code, response_json]
    else:
        return [request.status_code]
