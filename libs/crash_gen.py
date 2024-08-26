# =========================
# BEACONMC 1.19.4
# =========================
# Crash Generator
# (C) BeaconMC Team


import traceback
import os
import sys
import random
from datetime import datetime
from main import SERVER_VERSION

def gen_crash_report():
    with open(f"logs/crash_{datetime.timestamp( datetime.now() )}.txt", "w") as f:
        plugin_list = ""
        for p in os.listdir("plugins"):
            plugin_list += f"- {p}\n"
        f.write(f"""
=========================================
        BEACON-MC CRASH REPORT
=========================================
Something went wrong, please submit the report on the issue tracker.
Traceback :
{traceback.format_exc()}
=========================================
OS : {os.name}
Python Version : {sys.version}
BeaconMC Version : {SERVER_VERSION} 
Plugins List : 
{plugin_list}
Date : {datetime.now()}
=========================================
        """)
    f.close()
    print("\n")
    print("==========================================")
    print("BEACON-MC CRASH REPORT")
    print("> A crash report has been generated in the logs folder.")
    print("> Please submit the report on the issue tracker.")
    print("> Thank ^^")
    print("==========================================")
    exit(1)