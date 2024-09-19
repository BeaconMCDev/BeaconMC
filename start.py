# BeaconMC installation and boot file

# Import
import os

# DON'T TOUCH
VERSION = "Alpha-dev"

# Check structure
FILES_TO_CHECK = ["config.json", "main.py", "eula.txt", "LICENCE.md", "banned-ips.json", 
                "banned-players.json", "server-icon.png", "whitelist.json", "SECURITY.md", 
                "README.md", "requirements.txt", "utils/plugins/BeaconMCPlugin.py", "utils/locale/en_us.json", 
                "utils/locale/fr_fr.json", "utils/locale/es.json", "libs/crash_gen.py", "libs/mojangapi.py", 
                "libs/cryptography_system/system.py", "libs/cryptography_system/.private_key.pem", 
                "libs/cryptography_system/public_key.pem"]
FOLDERS_TO_CHECK = ["libs", "libs/cryptography_system", "crash_reports", "logs", "plugins", "utils", "worlds"]

state = "_DEFAULT"
missing_files = []
missing_folders = []
i = 0
j = 0

for file in FILES_TO_CHECK:
    if not(os.path.exists(file)):
        if state == "_DEFAULT":
            state = "_FILE_MISSING" 
        i += 1
        missing_files.append(file)

for folder in FOLDERS_TO_CHECK:
    if not(os.path.exists(folder)):
        if state == "_FILE_MISSING":
            state = "_FILE_AND_FOLDER_MISSING"
        if state == "_DEFAULT":
            state = "_FOLDER_MISSING"
        j += 1
        missing_folders.append(folder)

if state == "_FILE_MISSING":
    print("---------------------------------")
    print("WARNING : SOME FILES ARE MISSING !")
    print("PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases")
    print("---------------------------------")
    print(f"Missing files : {i} (list bellow)\n{missing_files}")
    print("---------------------------------")
elif state == "_FOLDER_MISSING":
    print("WARNING : SOME FOLDERS ARE MISSING !")
    print("PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases")
    print(f"Missing folders : {j} (list bellow)\n{missing_folders}")
elif state == "_FILE_AND_FOLDER_MISSING":
    print("WARNING : SOME FILES AND FOLDER ARE MISSING !")
    print("PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases")
    print(f"Missing files : {i} (list bellow)\n{missing_files}")
    print(f"Missing folders : {j} (list bellow)\n{missing_folders}")

if not(state == "_DEFAULT"):
    resp = input("Do you want to make this operation automatically ? You will need to restart this script once it will be done. (o/n)\nREQUIRE GIT INSTALLED, INSTALL THE LATEST VERSION AND MAY CAUSE ISSUE.\n-> ")
    if resp.lower() == "o":
        print("Installing...")
        os.system("git clone https://github.com/BeaconMCDev/BeaconMC.git")
        print("Done.")
    print("Process is terminating.")
    exit(-1)

# Check requirements
with open("requirements.txt", "r") as rf:
    line = None
    list_rq = []
    while line != "":
        line = rf.read()
        if line != "":
            list_rq.append(line)
    ...

# start
with open ("main.py", "r") as f:
    code = f.read()

exec(compile(code, 'main.py', 'exec'), {"__name__":"__start__"})