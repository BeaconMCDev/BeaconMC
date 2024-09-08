# BEACONMC 1.19.4
# =========================
# =========================
# Crash Generator
# (C) BeaconMC Team


import traceback
import os
import sys
import random
from datetime import datetime
import json

TOTAL_PLUGIN = 0
def gen_crash_report(SERVER_VERSION):
    global TOTAL_PLUGIN
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        online_mode = config["online_mode"]

    date_str = datetime.now().strftime("%m-%d-%Y")
    file_number = 1
    file_name = f"crash_reports/crash_{date_str}_{file_number}.txt"
    while os.path.exists(file_name):
        file_number += 1
        file_name = f"crash_reports/crash_{date_str}_{file_number}.txt"

    with open(file_name, "w") as f:

        plugin_list = ""
        for p in os.listdir("plugins"):
            plugin_list += f"- {p}\n"
            TOTAL_PLUGIN += 1
        json_info = json.dumps({"beaconmc_version": SERVER_VERSION,"os_name": os.name,"date": datetime.now().isoformat(),"python_version": sys.version,"total_plugin": TOTAL_PLUGIN,"traceback_error": traceback.format_exc()})
        f.write(f"""
=========================================
        BEACON-MC CRASH REPORT
=========================================
Something went wrong, please submit the report on the issue tracker.
https://github.com/BeaconMCDev/BeaconMC/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=
Traceback :
{traceback.format_exc()}
=========================================
OS : {os.name}
Python Version : {sys.version}
BeaconMC Version : {SERVER_VERSION} 
Plugins List : 
{plugin_list}
Date : {datetime.now()}

NOTE : Please **dont touch the error file if you want to use our debug tools !!!**
=========================================
JSON Info :
{json_info}
        """)
    f.close()
    print("\n")
    print("==========================================")
    print("BEACON-MC CRASH REPORT")
    print("> A crash report has been generated in the logs folder.")
    print("> Please submit the report on the issue tracker.")
    print("> Thank ^^")
    print("==========================================")
    print(f"Crash report saved on logs/{datetime.timestamp(datetime.now())}")

    print(f"ERR : {traceback.format_exc()}")
    exit(1)
