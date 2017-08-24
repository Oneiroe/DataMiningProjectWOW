"""
Algorithms to compute frequent itemsets of players inventory
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


###############################################
# A-PRIORI ALGORITHMs
##############

def a_priori_pass_1(input_file, threshold, output_file, bit_map):
    frequent_items = set()  # contains the frequent tuples
    item_count = {}  # intem_count[i]= #number of occurrences of item i

    baskets_number = 0
    avg_basket_length = 0

    # counting tuples occurrence in original file
    for line in input_file:
        baskets_number += 1
        splitted = line.split(' ')
        if '\n' in splitted: splitted.remove('\n')
        avg_basket_length += len(splitted)

        for item in splitted:

            if item in item_count:
                item_count[item] += 1
            else:
                item_count[item] = 1

    # filtering really frequent item element
    threshold_number = len(item_count) * threshold
    # threshold_number = 0
    for elem in item_count:
        bit_map[elem] = 0
        if int(item_count[elem]) >= threshold_number:
            frequent_items.add(elem)
            output_file.write(str(elem) + '\n')
            bit_map[elem] = 1

    avg_basket_length = 0
    if baskets_number != 0:
        avg_basket_length = int(avg_basket_length / baskets_number)

    print('#Frequent tuples:' + str(len(frequent_items)))
    print('#baskets:' + str(baskets_number))
    print('basket averange length:' + str(avg_basket_length))

    return [frequent_items, baskets_number, avg_basket_length]


def precedent_item_set(precedent_frequent, pas):
    item_count = {}

    perm_last_freq = itertools.combinations(precedent_frequent, pas)

    for perm in perm_last_freq:
        app = list()
        disjoin_tuple = itertools.chain(perm)
        for tup in disjoin_tuple:
            if len(app) > pas: break
            if pas > 2:
                disjoin_elem = itertools.chain(tup)
                for elem in disjoin_elem:
                    if elem not in app: app += [elem]
            else:
                if tup not in app: app += [tup]
        if len(app) > pas: continue
        app.sort(key=int)
        item_count[tuple(app)] = 0

    return item_count


def FAST_a_priori_pass_n(input_file, pas, threshold, item_count, output_file, bit_map):
    frequent_items = set()  # contains the frequent tuples

    for line in input_file:
        splitted = line.split(' ')
        if '\n' in splitted: splitted.remove('\n')
        for i in splitted:
            if bit_map[i] < pas - 1:
                splitted.remove(i)
        itemset = itertools.combinations(splitted, pas)

        for tupla in itemset:
            # increase the counter of the tuple
            if tupla in item_count:
                item_count[tupla] += 1

    # filtering really frequent tuple element
    for elem in item_count:
        if item_count[elem] >= threshold:
            frequent_items.add(elem)
            for j in elem:
                output_file.write(str(j) + ' ')
                bit_map[j] = pas
            output_file.write('\n')
    print('#Frequent tuples:' + str(len(frequent_items)))

    return frequent_items


def SUPER_FAST_a_priori_pass_n(input_file, pas, threshold, item_count, output_file, bit_map):
    frequent_items = set()  # contains the frequent tuples

    for line in input_file:
        splitted = line.split(' ')
        if '\n' in splitted: splitted.remove('\n')

        splitted = set(splitted)

        for tupla in item_count:
            # increase the counter of the tuple
            check = 0
            for item in tupla:
                if item not in splitted:
                    check = 1
                    break
            if check == 0:
                item_count[tupla] += 1

    # filtering really frequent tuple element
    for elem in item_count:
        if item_count[elem] >= threshold:
            frequent_items.add(elem)
            for j in elem:
                output_file.write(str(j) + ' ')
                bit_map[j] = pas
            output_file.write('\n')
    print('#Frequent tuples:' + str(len(frequent_items)))

    return frequent_items


def STATELESS_a_priori_n(input_file, pas, threshold, output_file, bit_map):
    frequent_items = set()  # contains the frequent tuples
    item_count = {}
    tstamp_one = time.time()
    with tqdm(total=235744) as pbar:
        for line in input_file:
            pbar.update(1)
            splitted = line.split(' ')
            if '\n' in splitted: splitted.remove('\n')
            for i in splitted:
                if bit_map[i] < pas - 1: splitted.remove(i)
            itemset = itertools.combinations(splitted, pas)

            for tupla in itemset:
                # increase the counter of the tuple
                item_count[tupla] = item_count.setdefault(tupla, 0) + 1
    print('time file scanning :' + str(time.time() - tstamp_one))

    tstamp_two = time.time()
    # filtering really frequent tuple element
    threshold_number = len(item_count) * threshold
    with tqdm(total=len(item_count)) as pbar:
        for elem in item_count:
            pbar.update(1)
            if item_count[elem] >= threshold_number:
                frequent_items.add(elem)
                for j in elem:
                    output_file.write(str(j) + ' ')
                    bit_map[j] = pas
                output_file.write('\n')
    print('time filtering:' + str(time.time() - tstamp_two))

    print('#Frequent tuples:' + str(len(frequent_items)))

    return frequent_items


# TODO normalize in and out file: here IN is assumed as already open, while OUT is opened by the function
def a_priori(input_file, output_file, threshold):
    # respectivelly: file to examinate;number of passes(singleton, pair, triple,...); threshold
    frequent_tuples = []
    output_file = open(output_file, 'w')
    bit_map = {}

    # first pass
    print('**********************\nPASS 1')
    tstamp = time.time()

    app_ris = a_priori_pass_1(input_file, threshold, output_file, bit_map)
    frequent_tuples += [app_ris[0]]
    baskets_number = app_ris[1]
    avg_basket_length = app_ris[2]

    print('time:' + str(time.time() - tstamp))
    print('**********************')

    # other passes
    last_cost_sign = -1
    pas = 2
    while 1:
        print('**********************\nPASS ' + str(pas))
        tstamp_start = time.time()
        tstamp = time.time()

        # look if going through stupid algorithm or not
        print('c_stupid...')
        c_stupid = 1
        # c_stupid = baskets_number * (
        #     math.factorial(avg_basket_length) / (math.factorial(pas) * math.factorial(avg_basket_length - pas)))
        print('...time:' + str(time.time() - tstamp))
        tstamp = time.time()
        print('c_other...')
        # c_other = (math.factorial(len(frequent_tuples[pas - 2])) / (
        #     math.factorial(pas) * math.factorial(len(frequent_tuples[pas - 2]) - pas)))
        c_other = 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
        print('...time:' + str(time.time() - tstamp))
        tstamp = time.time()
        greatness_factor = 1
        if c_stupid < (c_other * greatness_factor):
            print('stupid')
            input_file.seek(0)
            frequent_tuples += [STATELESS_a_priori_n(input_file, pas, threshold, output_file, bit_map)]
            if len(frequent_tuples[-1]) < pas + 1:
                print('time:' + str(time.time() - tstamp))
                break
            pas += 1
            print('time:' + str(time.time() - tstamp))
            print('**********************')
            continue

        print('other')
        # computing precedent frequent items tuples
        tA = time.time()

        item_count = precedent_item_set(frequent_tuples[pas - 2], pas)

        tA = time.time() - tA
        # ~ print 'A-TIME:'+str(tA)
        # ~ print 'PAPABILI:'+str(len(item_count))
        if len(item_count) < pas + 1:
            print('time:' + str(time.time() - tstamp))
            break

        # recompute costs
        # ~ if last_cost_sign<0:
        # calculate costs: c(FAST)-c(SUPER)
        prec_freq_len = len(frequent_tuples[pas - 2])
        papabili_num = len(item_count)
        if pas == 2:
            t = 2
        else:
            t = pas * (pas - 1)
        c_fast = avg_basket_length + (
            math.factorial(avg_basket_length) / (math.factorial(pas) * math.factorial(avg_basket_length - pas)))
        c_super = papabili_num * pas
        cost = c_fast - c_super
        # ~ if cost>=0: last_cost_sign=1

        # counting tuples occurrence in original file
        tB = time.time()
        input_file.seek(0)
        # ~ if last_cost_sign<0:
        if cost < 0:
            frequent_tuples += [FAST_a_priori_pass_n(input_file, pas, threshold, item_count, output_file, bit_map)]
        else:
            frequent_tuples += [
                SUPER_FAST_a_priori_pass_n(input_file, pas, threshold, item_count, output_file, bit_map)]

        tB = time.time() - tB
        # ~ print( 'B-TIME:'+str(tB))


        # ~ if len(frequent_tuples[-1])==0:
        if len(frequent_tuples[-1]) < pas + 1:
            print('time:' + str(time.time() - tstamp))
            break
        pas += 1
        print('time:' + str(time.time() - tstamp))
        print('**********************')
    output_file.close()
    return frequent_tuples


###############################################
# PREPROCESSING
##############
def create_locale_characters_itemsets(region, locale, DB_BASE_PATH, output):
    """ Create a file containing only players items itemset for the given locale """
    logging.debug('create_locale_characters_itemsets(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    ITEM_CLASSES_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'item', 'item_classes.json')
    fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}
    # fields=set()
    # PREPROCESSING
    with open(output, 'w') as itemset_file:
        with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
            for file in os.listdir(CHARACTER_PATH):
                pbar.update(1)
                if not file.endswith('.json'):
                    continue
                with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                    try:
                        character_json = json.load(character_file)
                        try:
                            # like this we are not distinguish between items category, just caring about itemset
                            character_equipment = []
                            for field in character_json['items']:
                                if field in fields_to_skip:
                                    continue
                                # fields.add(field)
                                character_equipment.append(character_json['items'][field]['id'])
                            itemset_file.writelines(str(i) + ' ' for i in character_equipment)
                            # itemset_file.write(os.linesep)
                            itemset_file.write('\n')
                        except KeyError as err:
                            logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                            logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    except json.decoder.JSONDecodeError as err:
                        # Probable incomplete or wrongly downloaded data, retry
                        logging.warning(
                            'JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                        continue


def join_locales_characters_itemets(results_path, output_path):
    """ Join in a single file the itemsets of al the locales """
    logging.debug('join_locales_characters_itemets()')
    with tqdm(total=12) as pbar:
        with open(output_path, 'w') as outfile:
            for file in os.listdir(results_path):
                if (not file.startswith('itemsets_')) \
                        or (not file.endswith('.dat')) \
                        or ('_lv_' in file) \
                        or ('_class_' in file):
                    continue
                pbar.update(1)
                with open(os.path.join(results_path, file)) as items_file:
                    for line in items_file:
                        if not line == '\n':
                            outfile.write(line)


def create_level_locale_characters_itemsets(region, locale, DB_BASE_PATH, output_base_path):
    """ Create players' items itemsets from the given locale, grouping per level (10 lv per group) """
    logging.debug('create_level_locale_characters_itemsets(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    ITEM_CLASSES_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'item', 'item_classes.json')
    fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}
    # fields=set()
    # PREPROCESSING
    output_array = [
        open(os.path.join(output_base_path, 'itemsets_' + region + '_' + locale + '_lv_' + str(level) + '.dat'), 'w')
        for level in range(0, 111, 10)]
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        # like this we are not distinguish between items category, just caring about itemset
                        character_equipment = []
                        for field in character_json['items']:
                            if field in fields_to_skip:
                                continue
                            # fields.add(field)
                            character_equipment.append(character_json['items'][field]['id'])
                        character_level = character_json['level']
                        output_array[int(character_level / 10)].writelines(str(i) + ' ' for i in character_equipment)
                        # itemset_file.write(os.linesep)
                        output_array[int(character_level / 10)].write('\n')
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(
                            sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning(
                        'JSONDecodeError: ' + str(err) + ' -- line: ' + str(
                            sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    for i in output_array:
        i.close()


def join_level_locale_characters_itemets(results_path, output_base_path):
    """ Join in a single files the itemsets of all the locales per lavel"""
    logging.debug('join_level_locale_characters_itemets()')
    output_array = [
        open(os.path.join(output_base_path, 'total_itemsets_lv_' + str(level) + '.dat'), 'w')
        for level in range(0, 111, 10)]
    with tqdm(total=12 * 12) as pbar:
        for file in os.listdir(results_path):
            if (not file.startswith('itemsets_')) \
                    or (not file.endswith('.dat')) \
                    or ('_lv_' not in file) \
                    or ('_class_' in file):
                continue
            pbar.update(1)
            with open(os.path.join(results_path, file)) as items_file:
                file_level = int(file.split('lv_')[1][:-4])
                for line in items_file:
                    if not line == '\n':
                        output_array[int(file_level / 10)].write(line)
    for i in output_array:
        i.close()


def create_class_level_locale_characters_itemsets(region, locale, DB_BASE_PATH, output_base_path):
    """ Create players' items itemsets from the given locale, grouping per class and level (10 lv per group) """
    logging.debug('create_class_level_locale_characters_itemsets(' + region + ', ' + locale + ')')

    DB_LOCALE_PATH = os.path.join(DB_BASE_PATH, region, locale)
    CHARACTER_PATH = os.path.join(DB_LOCALE_PATH, 'character')
    ITEM_CLASSES_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'item', 'item_classes.json')
    fields_to_skip = {'averageItemLevel', 'averageItemLevelEquipped'}
    # fields=set()
    # PREPROCESSING
    CLASS_PATH = os.path.join(DB_LOCALE_PATH, 'data', 'character', 'classes')

    classes = []
    # Find all classes
    with open(os.path.join(CLASS_PATH, 'classes.json')) as classes_file:
        try:
            classes_json = json.load(classes_file)
            try:
                for character_class in classes_json['classes']:
                    classes.append(character_class['id'])
            except KeyError as err:
                logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
                logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))
        except json.decoder.JSONDecodeError as err:
            # Probable incomplete or wrongly downloaded data, retry
            logging.warning('JSONDecodeError: ' + str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
            logging.warning(str(os.path.join(CLASS_PATH, 'classes.json')))

    output_map = {}
    for character_class in classes:
        output_map[character_class] = [
            open(os.path.join(output_base_path,
                              'itemsets_' + region + '_' + locale + '_lv_' + str(level) + '_class_' + str(
                                  character_class) + '.dat'), 'w') for level in range(0, 111, 10)]
    with tqdm(total=len(os.listdir(CHARACTER_PATH))) as pbar:
        for file in os.listdir(CHARACTER_PATH):
            pbar.update(1)
            if not file.endswith('.json'):
                continue
            with open(os.path.join(CHARACTER_PATH, file)) as character_file:
                try:
                    character_json = json.load(character_file)
                    try:
                        # like this we are not distinguish between items category, just caring about itemset
                        character_equipment = []
                        for field in character_json['items']:
                            if field in fields_to_skip:
                                continue
                            # fields.add(field)
                            character_equipment.append(character_json['items'][field]['id'])
                        character_level = character_json['level']
                        output_map[character_json['class']][int(character_level / 10)].writelines(
                            str(i) + ' ' for i in character_equipment)
                        # itemset_file.write(os.linesep)
                        output_map[character_json['class']][int(character_level / 10)].write('\n')
                    except KeyError as err:
                        logging.warning('KeyError: ' + str(err) + ' -- line: ' + str(
                            sys.exc_info()[-1].tb_lineno))
                        logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                except json.decoder.JSONDecodeError as err:
                    # Probable incomplete or wrongly downloaded data, retry
                    logging.warning(
                        'JSONDecodeError: ' + str(err) + ' -- line: ' + str(
                            sys.exc_info()[-1].tb_lineno))
                    logging.warning(str(os.path.join(CHARACTER_PATH, file)))
                    continue
    for character_class in output_map:
        for i in output_map[character_class]:
            i.close()


def join_class_level_locale_characters_itemets(results_path, output_base_path, classes):
    """ Join in a single files the itemsets of all the locales per class and  lavel"""
    logging.debug('join_class_level_locale_characters_itemets()')

    output_map = {}
    for character_class in classes:
        output_map[character_class] = [
            open(os.path.join(output_base_path, 'total_itemsets_lv_' + str(level) + '_class_' + str(
                character_class) + '.dat'), 'w')
            for level in range(0, 111, 10)]
    with tqdm(total=12 * 12 * 12) as pbar:
        for file in os.listdir(results_path):
            if (not file.startswith('itemsets_')) \
                    or (not file.endswith('.dat')) \
                    or ('_lv_' not in file) \
                    or ('_class_' not in file):
                continue
            pbar.update(1)
            with open(os.path.join(results_path, file)) as items_file:
                file_level = int(file.split('lv_')[1].split('_')[0])
                file_character_class = int(file.split('class_')[1][:-4])
                for line in items_file:
                    if not line == '\n':
                        output_map[file_character_class][int(file_level / 10)].write(line)
    for character_class in output_map:
        for i in output_map[character_class]:
            i.close()


def create_all_itemsets_one_pass(locales_map, DB_BASE_PATH, output_base_path, classes):
    """ Create all the itemsets (general, total, per locale, level, class,...) scanning the dataset only once. """
    # TODO
    return


###############################################
# TEST-MAIN
##############
def main():
    pass


if __name__ == "__main__":
    main()
