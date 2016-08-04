##### WoWspider
# For each API call (functions of WoWrapper), extracts from the responses the info needed to retrieve other data


import requests
import os
import json
import time
import logging
import types
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
LAST_CALL_TIMESTAMP = 0  # last api call timestamp
MIN_TIME_LAPSE = 1 / (LIMIT_CALL_PER_HOUR / 3600)


##################
#### API CALL ####

# search in a json_file the requested key. Returns a dictionary that pairs kay to found values
# def search_for(json_file, keys):
#     # TODO ? -> PROBLEM a general key like "id" may match wrong value in this auto-search
#     logging.info('SEARCHING in "' + json_file + '" for :' + keys)
#     file = open(json_file, 'r')
#     json_file = json.load(file)
#
#     if isinstance(json_file, dict):
#         for key in json_file.keys():
#             pass
#     elif isinstance(json_file, list):
#         for elem in json_file:
#             pass


###########################
#### WRAPPER FUNCTIONS ####
# the following function generate the request link for the API

#####################
#### ACHIEVEMENT ####

# Achievement -> reward_item
def search_in_achievement(file_path):
    logging.debug('search_in_achievement(' + file_path + ')')
    result = {'item_id': set()}

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # retrieve reward item
        for item in json_file['rewardItems']:
            try:
                result['item_id'].add(item['id'])
            except KeyError:
                pass
        return result


#################
#### AUCTION ####

# Auctions -> item, character, realm
def search_in_auction(file_path):
    logging.debug('search_in_auction(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'character_name': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        for auc in json_file['auctions']:
            try:
                result['item_id'].add(auc['item'])
            except KeyError:
                pass
            try:
                result['character'].add(auc['owner'] + ',' + auc['ownerRealm'])
                result['character_name'].add(auc['owner'])
                result['realm'].add(auc['ownerRealm'])
            except KeyError:
                pass
        return result


##############
#### BOSS ####

# boss_masterlist -> boss, zone
def search_in_boss_masterlist(file_path):
    logging.debug('search_in_boss_masterlist(' + file_path + ')')
    result = {'boss_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for boss in json_file['bosses']:
                try:
                    result['boss_id'].add(boss['id'])
                except KeyError:
                    pass
                try:
                    for npc in boss['npcs']:
                        result['boss_id'].add(npc['id'])
                except KeyError:
                    pass
                try:
                    result['zone_id'].add(boss['zoneId'])
                except KeyError:
                    pass
        except KeyError:
            pass
        return result


# boss -> zone
def search_in_boss(file_path):
    logging.debug('search_in_boss(' + file_path + ')')
    result = {'zone_id': set()}

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            result['zone_id'].add(json_file['zoneId'])
        except KeyError:
            pass
        return result


###################
#### CHALLENGE ####

# The data in this request has data for all 9 challenge mode maps (currently).
# The map field includes the current medal times for each dungeon.
# Inside each ladder we provide data about each character that was part of each run.
# The character data includes the current cached spec of the character
# while the member field includes the spec of the character during the challenge mode run.
def search_in_realm_leaderboard(file_path):
    logging.debug('search_in_realm_leaderboard(' + file_path + ')')
    result = {'character': set(),
              'realm': set(),
              'character_name': set(),
              'guild': set(),  # CSV guild_name, realm
              'guild_name': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for challenge in json_file['challenge']:

                try:
                    result['realm'].add(challenge['realm']['slug'])
                    for realm in challenge['realm']['connected_realms']:
                        result['realm'].add(realm)
                except KeyError:
                    pass

                result['realm'].add(challenge['map']['slug'])

                for group in challenge['groups']:
                    for member in group['members']:
                        try:
                            result['character'].add(member['character']['name'] + ',' + member['character']['realm'])
                            result['character_name'].add(member['character']['name'])
                            result['realm'].add(member['character']['realm'])
                        except KeyError:
                            pass
                        try:
                            result['guild'].add(member['character']['guild'] + ',' + member['character']['guildRealm'])
                            result['guild_name'].add(member['character']['guild'])
                            result['realm'].add(member['character']['guildRealm'])
                        except KeyError:
                            pass

        except KeyError:
            pass
        return result


# The region leaderboard has the exact same data format as the realm leaderboards except there is no realm field.
# It is simply the top 100 results gathered for each map for all of the available realm leaderboards in a region.
def search_in_region_leaderboard(file_path):
    logging.debug('search_in_region_leaderboard(' + file_path + ')')
    result = {'character': set(),
              'realm': set(),
              'character_name': set(),
              'guild': set(),  # CSV guild_name, realm
              'guild_name': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for challenge in json_file['challenge']:
                result['realm'].add(challenge['map']['slug'])

                for group in challenge['groups']:
                    for member in group['members']:
                        try:
                            result['character'].add(member['character']['name'] + ',' + member['character']['realm'])
                            result['character_name'].add(member['character']['name'])
                            result['realm'].add(member['character']['realm'])
                        except KeyError:
                            pass
                        try:
                            result['guild'].add(member['character']['guild'] + ',' + member['character']['guildRealm'])
                            result['guild_name'].add(member['character']['guild'])
                            result['realm'].add(member['character']['guildRealm'])
                        except KeyError:
                            pass

        except KeyError:
            pass
        return result


###################
#### CHARACTER ####

# The Character Profile API is the primary way to access character information.
# This Character Profile API can be used to fetch a single character at a time through an HTTP GET request
# to a URL describing the character profile resource.
# By default,a basic dataset will be returned and with each request and zero or more additional fields can be retrieved.
# To access this API, craft a resource URL pointing to the character who's information is to be retrieved.

# Retrieve character basic info
# # TODO
# def search_in_character(file_path):
#     logging.info('search_in_auction(' + file_path + ')')
#     result = {'item_id': set(),
#               'character': set(),
#               'realm': set(),
#               'boss_id': set(),
#               'character_name': set(),
#               'guild_name': set(),
#               'pet_ability_id': set(),
#               'species_id': set(),
#               'quest_id': set(),
#               'recipe_id': set(),
#               'spell_id': set(),
#               'zone_id': set(),
#               }
#
#     try:
#         f = open(file_path, 'r')
#         json_file = json.load(f)
#     except json.JSONDecodeError as err:
#         # error decoding json
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     except OSError as err:
#         # error reading file
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     else:
#         return result


# Retrieve character selected fields info
#  TODO
# def search_in_character_selected_fileds(file_path):
#     logging.info('search_in_auction(' + file_path + ')')
#     result = {'item_id': set(),
#               'character': set(),
#               'realm': set(),
#               'boss_id': set(),
#               'character_name': set(),
#               'guild_name': set(),
#               'pet_ability_id': set(),
#               'species_id': set(),
#               'quest_id': set(),
#               'recipe_id': set(),
#               'spell_id': set(),
#               'zone_id': set(),
#               }
#
#     try:
#         f = open(file_path, 'r')
#         json_file = json.load(f)
#     except json.JSONDecodeError as err:
#         # error decoding json
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     except OSError as err:
#         # error reading file
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     else:
#
#         return result


# Retrieve character full info at once
def search_in_character_full(file_path):
    logging.debug('search_in_character_full(' + file_path + ')')
    result = {'item_id': set(),
              'realm': set(),
              'guild': set(),  # CSV guild_name, realm
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            # ITEM EQUIPED
            for slot in json_file['items'].keys():
                if (slot == 'averageItemLevel') or (slot == 'averageItemLevelEquipped'):
                    continue
                try:
                    result['item_id'].add(json_file['items'][slot]['id'])
                except KeyError:
                    pass
        except KeyError:
            pass
        try:
            # PET ABILITY
            for slot in json_file['petSlots']:
                try:
                    for ability in slot['abilities']:
                        result['pet_ability_id'].add(ability)
                except KeyError:
                    pass
        except KeyError:
            pass
        try:
            # RECIPES
            for primary in json_file['professions']['primary']:
                try:
                    for recipe in primary['recipes']:
                        result['recipe_id'].add(recipe)
                except KeyError:
                    pass
            for secondary in json_file['professions']['secondary']:
                try:
                    for recipe in secondary['recipes']:
                        result['recipe_id'].add(recipe)
                except KeyError:
                    pass
        except KeyError:
            pass

        try:
            # QUESTS
            for quest in json_file['quests']:
                result['quest_id'].add(quest)
        except KeyError:
            pass

        #try:
        #    # SPELL FROM TALENT
        #    logging.warning('SPELL FROM TALENTS')
        #    for app in json_file['talents']:
        #        for talent in app['talents']:
        #            for app_due in talent:
        #                for app_tre in app_due:
        #                    for tier in app_tre:
        #                        result['spell_id'].add(tier['spell']['id'])
        #except KeyError:
        #    pass

        try:
            # GUILD
            result['guild'].add(json_file['guild']['name'] + ',' + json_file['guild']['realm'])
            result['guild_name'].add(json_file['guild']['name'])
            result['realm'].add(json_file['guild']['realm'])
        except KeyError:
            pass
    return result


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
# def search_in_guild(file_path):
#     # TODO
#     logging.info('search_in_auction(' + file_path + ')')
#     result = {'item_id': set(),
#               'character': set(),
#               'realm': set(),
#               'boss_id': set(),
#               'character_name': set(),
#               'guild_name': set(),
#               'pet_ability_id': set(),
#               'species_id': set(),
#               'quest_id': set(),
#               'recipe_id': set(),
#               'spell_id': set(),
#               'zone_id': set(),
#               }
#
#     try:
#         f = open(file_path, 'r')
#         json_file = json.load(f)
#     except json.JSONDecodeError as err:
#         # error decoding json
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     except OSError as err:
#         # error reading file
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     else:
#         return result


# Retrieve guild selected fields info
# def search_in_guild_selected_fields(file_path):
#     # TODO
#     logging.info('search_in_auction(' + file_path + ')')
#     result = {'item_id': set(),
#               'character': set(),
#               'realm': set(),
#               'boss_id': set(),
#               'character_name': set(),
#               'guild_name': set(),
#               'pet_ability_id': set(),
#               'species_id': set(),
#               'quest_id': set(),
#               'recipe_id': set(),
#               'spell_id': set(),
#               'zone_id': set(),
#               }
#
#     try:
#         f = open(file_path, 'r')
#         json_file = json.load(f)
#     except json.JSONDecodeError as err:
#         # error decoding json
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     except OSError as err:
#         # error reading file
#         logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
#         return {}
#     else:
#         return result


# Retrieve guild full info at once
def search_in_guild_full(file_path):
    logging.debug('search_in_guild_full(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            # CHALLENGE
            logging.warning('CHALLENGE')
            for challenge in json_file['challenge']:
                try:
                    result['realm'].add(challenge['realm']['slug'])
                    for realm in challenge['realm']['connected_realms']:
                        result['realm'].add(realm)
                except KeyError:
                    pass

                result['realm'].add(challenge['map']['slug'])

                for group in challenge['groups']:
                    for member in group['members']:
                        try:
                            result['character'].add(member['character']['name'] + ',' + member['character']['realm'])
                            result['character_name'].add(member['character']['name'])
                            result['realm'].add(member['character']['realm'])
                        except KeyError:
                            pass
                        try:
                            result['guild'].add(member['character']['guild'] + ',' + member['character']['guildRealm'])
                            result['guild_name'].add(member['character']['guild'])
                            result['realm'].add(member['character']['guildRealm'])
                        except KeyError:
                            pass
            # MEMBERS
            for member in json_file['members']:
                try:
                    result['character_name'].add(member['character']['name'])
                    result['realm'].add(member['character']['realm'])
                    result['character'].add(member['character']['name'] + ',' + member['character']['realm'])
                except KeyError:
                    pass

            # NEWS
            for news in json_file['news']:
                try:
                    result['item_id'].add(news['itemId'])
                except KeyError:
                    pass
        except KeyError:
            pass
        return result


##############
#### ITEM ####

# The item API provides detailed item information. This includes item set information if this item is part of a set.
def search_in_item(file_path):
    logging.debug('search_in_item(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              'item_set_id': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            # SPELL
            for spell in json_file['itemSpells']:
                result['spell_id'].add(spell['spellId'])
        except KeyError:
            pass
        try:
            # ITEM-SET
            result['item_set_id'].add(json_file['itemSet']['id'])
        except KeyError:
            pass
        return result


# This provides item set information.
def search_in_item_set(file_path):
    logging.debug('search_in_item_set(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for item in json_file['items']:
                result['item_id'].add(item)
        except KeyError:
            pass
        return result


###############
#### MOUNT ####

# A list of all supported mounts.
def search_in_mount_masterlist(file_path):
    logging.debug('search_in_mount_masterlist(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for mount in json_file['mounts']:
                result['spell_id'].add(mount['spellId'])
                result['item_id'].add(mount['itemId'])
        except KeyError:
            pass
        return result


#############
#### PET ####

# A list of all supported battle and vanity pets.
def search_in_pet_masterlist(file_path):
    logging.debug('search_in_pet_masterlist(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for pet in json_file['pets']:
                result['species_id'].add(pet['stats']['speciesId'])
        except KeyError:
            pass
        return result


# This provides data about a individual battle pet ability ID. We do not provide the tooltip for the ability yet.
# We are working on a better way to provide this since it depends on your pet's species, level and quality rolls.
def search_in_pet_ability(file_path):
    logging.debug('search_in_pet_ability(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # noting to return
        return {}


# This provides the data about an individual pet species.
# The species IDs can be found your character profile using the options pets field.
# Each species also has data about what it's 6 abilities are.
def search_in_pet_species(file_path):
    logging.debug('search_in_pet_species(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for ability in json_file['abilities']:
                result['pet_ability_id'].add(ability['id'])
        except KeyError:
            pass
        return result


# Retrieve detailed information about a given species of pet.
def search_in_pet_species_stat(file_path):
    logging.debug('search_in_pet_species_stat(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


#############
#### PVP ####

# The Leaderboard API endpoint provides leaderboard information for the 2v2,3v3,5v5 and Rated Battleground leaderboards.
def search_in_pvp_leaderboard(file_path):
    logging.debug('search_in_pvp_leaderboard(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for row in json_file['rows']:
                try:
                    result['character_name'].add(row['name'])
                    result['realm'].add(row['realmSlug'])
                    result['character'].add(row['name'] + ',' + row['realmSlug'])
                except KeyError:
                    pass
        except KeyError:
            pass
        return result


###############
#### QUEST ####

# Retrieve metadata for a given quest.
def search_in_quest(file_path):
    logging.debug('search_in_quest(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


###############
#### REALM ####

# The realm status API allows developers to retrieve realm status information.
# This information is limited to whether or not the realm is up, the type and state of the realm,
# the current population, and the status of the two world PvP zones.

# There are no required query string parameters when accessing this resource,
# although the optional realms parameter can be used to limit the realms returned to a specific set of realms.

def search_in_realm_status(file_path):
    logging.debug('search_in_realm_status(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for realm in json_file['realms']:
                try:
                    result['realm'].add(realm['slug'])
                    for connected in realm['connected_realms']:
                        result['realm'].add(connected)
                except KeyError:
                    pass
        except KeyError:
            pass
        return result


################
#### RECIPE ####

# The recipe API provides basic recipe information.
def search_in_recipe(file_path):
    logging.debug('search_in_recipe(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


###############
#### SPELL ####

# The spell API provides some information about spells.
def search_in_spell(file_path):
    logging.debug('search_in_spell(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


##############
#### ZONE ####

# A list of all supported zones and their bosses.
# A 'zone' in this context should be considered a dungeon, or a raid, not a zone as in a world zone.
# A 'boss' in this context should be considered a boss encounter, which may include more than one NPC.
def search_in_zone_masterlist(file_path):
    logging.debug('search_in_zone_masterlist(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for zone in json_file['zones']:
                result['zone_id'].add(zone['id'])
        except KeyError:
            pass
        return result


# The Zone API provides some information about zones.
def search_in_zone(file_path):
    logging.debug('search_in_zone(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


##############
#### DATA ####

# The battlegroups data API provides the list of battlegroups for this region. Please note the trailing / on this URL.
def search_in_data_battlegroups(file_path):
    logging.debug('search_in_data_battlegroups(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


# The character races data API provides a list of each race and their associated faction, name, unique ID, and skin.
def search_in_data_races(file_path):
    logging.debug('search_in_data_races(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


# The character classes data API provides a list of character classes.
def search_in_data_classes(file_path):
    logging.debug('search_in_data_classes(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing to return
        return {}


# The character achievements data API provides a list of all of the achievements
# that characters can earn as well as the category structure and hierarchy.
def search_in_data_achievements(file_path):
    logging.debug('search_in_data_achievements(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              'achievement_id': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for kind in json_file['achievements']:
                try:
                    for achievement in kind['achievements']:
                        try:
                            result['achievement_id'].add(achievement['id'])
                        except KeyError:
                            pass
                        try:
                            for reward in achievement['rewardItems']:
                                result['item_id'].add(reward['id'])
                        except KeyError:
                            pass
                except KeyError:
                    pass
                for category in kind['categories']:
                    try:
                        for achievement in category['achievements']:
                            try:
                                result['achievement_id'].add(achievement['id'])
                            except KeyError:
                                pass
                            try:
                                for reward in achievement['rewardItems']:
                                    result['item_id'].add(reward['id'])
                            except KeyError:
                                pass
                    except KeyError:
                        pass
        except KeyError:
            pass
        return result


# The guild rewards data API provides a list of all guild rewards.
def search_in_data_guild_rewards(file_path):
    logging.debug('search_in_data_guild_rewards(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for reward in json_file['rewards']:
                result['item_id'].add(reward['item']['id'])
        except KeyError:
            pass
        return result


# The guild perks data API provides a list of all guild perks.
def search_in_data_guild_perks(file_path):
    logging.debug('search_in_data_guild_perks(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for perk in json_file['perks']:
                try:
                    result['spell_id'].add(perk['spell']['id'])
                except KeyError:
                    pass
        except KeyError:
            pass
        return result


# The guild achievements data API provides a list of all of the achievements
# that guilds can earn as well as the category structure and hierarchy.
def search_in_data_guild_achievements(file_path):
    logging.debug('search_in_data_guild_achievements(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              'achievement_id': set()
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for kind in json_file['achievements']:
                for achievement in kind['achievements']:
                    try:
                        result['achievement_id'].add(achievement['id'])
                    except KeyError:
                        pass
                    try:
                        for reward in achievement['rewardItems']:
                            result['item_id'].add(reward['id'])
                    except KeyError:
                        pass
        except KeyError:
            pass
        return result


# The item classes data API provides a list of item classes
def search_in_data_item_classes(file_path):
    logging.debug('search_in_data_item_classes(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        # nothing ro return
        return {}


# The talents data API provides a list of talents, specs and glyphs for each class.
def search_in_data_talents(file_path):
    logging.debug('search_in_data_talents(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for k in json_file.keys():
                # SPELL FROM TALENT
                for app_talents in json_file[k]['talents']:
                    for appo in app_talents:
                        for app_due in appo:
                            # for app_tre in app_due:
                            result['spell_id'].add(app_due['spell']['id'])
        except KeyError:
            pass
    return result  # The different bat pet types (including what they are strong and weak against)


# The different bat pet types (including what they are strong and weak against)
def search_in_data_pet_types(file_path):
    logging.debug('search_in_data_pet_types(' + file_path + ')')
    result = {'item_id': set(),
              'character': set(),
              'realm': set(),
              'boss_id': set(),
              'character_name': set(),
              'guild_name': set(),
              'pet_ability_id': set(),
              'species_id': set(),
              'quest_id': set(),
              'recipe_id': set(),
              'spell_id': set(),
              'zone_id': set(),
              }

    try:
        f = open(file_path, 'r')
        json_file = json.load(f)
    except json.JSONDecodeError as err:
        # error decoding json
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    except OSError as err:
        # error reading file
        logging.warning(str(err)+' -- line: '+str(sys.exc_info()[-1].tb_lineno))
        return {}
    else:
        try:
            for type in json_file['petTypes']:
                result['pet_ability_id'].add(type['typeAbilityId'])
        except KeyError:
            pass
        return result
