##### controller
# it starts the processes, and managing the space on device suspend them

import psutil
import os
import subprocess
import time
import sys

###############
# TO-DO

# TODO Demonize this script (manually start,stop,pause from command line)
###############

DB_BASE_PATH = os.path.join(os.getcwd(), 'DB', 'WOW')

print('Start Controller')

# START CRAWLER and GET PID
pid = subprocess.Popen('python3 WoWcawler.py', shell=True).pid
# os.system("nohup python3 WoWcawler.py &")
if not psutil.pid_exists(pid):
    print('PID doesn\'t exists')
    exit()

print('Launched WoWcawler.py --> PID: ' + str(pid))

process = psutil.Process(pid) + 1

# ANALYSE SPACE LEFT
while process.status() == 'running':
    # Do nothing until memory is full at 95%
    while psutil.disk_usage('.')[-1] < 90:  # percent occupied space
        time.sleep(60)
        continue

    print('Memory load > 90% --> ' + str(psutil.disk_usage('.')[-1]))

    # Suspend the process and wait till free memory is restored
    process.suspend()
    print('Process suspended')

    # WAIT FILE DOWNLOADING FROM SERVER TO LOCAL STORAGE
    # a flag file is created and the program waits till it's manually removed
    print('Waiting for DB download')

    open('DOWNLOAD_FLAG', 'w').close()
    while os.path.exists('DOWNLOAD_FLAG'):
        time.sleep(60)

    print('Freeing space...')
    # Truncate DB file content
    try:
        for dirname, dirnames, filenames in os.walk(DB_BASE_PATH):
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
        continue
    print('...DONE --> usage: ' + str(psutil.disk_usage('.')[-1]))

    # Resume the process
    process.resume()
    print('Process resumed')
