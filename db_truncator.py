##### controller
# it starts the processes, and managing the space on device suspend them

import psutil
import os
import time
import sys

DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')

print('Truncating DB objects...')
# Truncate DB file content
try:
    for dirname, dirnames, filenames in os.walk(DB_BASE_PATH):
        if dirname.__contains__('data'):
            continue
        print(dirname)
        for filename in filenames:
            try:
                if filename.endswith('.json'):
                    file_path = os.path.join(dirname, filename)
                    os.truncate(file_path, 0)
            except os.error as err:
                print(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
except os.error as err:
    print(str(err) + ' -- line: ' + str(sys.exc_info()[-1].tb_lineno))
    time.sleep(60)
print('...DONE --> usage: ' + str(psutil.disk_usage('.')[-1]))