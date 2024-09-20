import os

FILES = ["config.json", "pluginapi.py", "main.py", "eula.txt", "LICENCE.md", "banned-ips.json", 
                "banned-players.json", "server-icon.png", "whitelist.json", "SECURITY.md", 
                "README.md", "requirements.txt", "utils/plugins/BeaconMCPlugin.py", "utils/locale/en_us.json", 
                "utils/locale/fr_fr.json", "utils/locale/es.json", "libs/crash_gen.py", "libs/mojangapi.py", 
                "libs/cryptography_system/system.py"]

files_content = {
    "main.py": open("main.py").read(),
    "pluginapi.py": open("pluginapi.py").read(),
    "config.json": open("config.json").read(),
    "eula.txt": open("eula.txt").read(),
    "LICENCE.md": open("LICENCE.md").read(),
    "banned-ips.json": open("banned-ips.json").read(),
    "banned-players.json": open("banned-players.json").read(),
    "server-icon.png": open("server-icon.png", "rb").read(),  # Fichier binaire
    "whitelist.json": open("whitelist.json").read(),
    "SECURITY.md": open("SECURITY.md").read(),
    "README.md": open("README.md").read(),
    "requirements.txt": open("requirements.txt").read(),
    "utils/plugins/BeaconMCPlugin.py": open("utils/plugins/BeaconMCPlugin.py").read(),
    "utils/locale/en_us.json": open("utils/locale/en_us.json").read(),
    "utils/locale/fr_fr.json": open("utils/locale/fr_fr.json").read(),
    "utils/locale/es.json": open("utils/locale/es.json").read(),
    "libs/crash_gen.py": open("libs/crash_gen.py").read(),
    "libs/mojangapi.py": open("libs/mojangapi.py").read(),
    "libs/cryptography_system/system.py": open("libs/cryptography_system/system.py").read()
}

dico = "{"

for f in FILES:
    dico += f'"{f}":"""{files_content[f]}""", \n'
dico = dico[:3]

template = """# BeaconMC installation and boot file

# Import
import os

# DON'T TOUCH
VERSION = "Alpha-dev"
dico = {0}

# Check structure
FILES_TO_CHECK = ["config.json", "pluginapi.py", "main.py", "eula.txt", "LICENCE.md", "banned-ips.json", 
                "banned-players.json", "server-icon.png", "whitelist.json", "SECURITY.md", 
                "README.md", "requirements.txt", "utils/plugins/BeaconMCPlugin.py", "utils/locale/en_us.json", 
                "utils/locale/fr_fr.json", "utils/locale/es.json", "libs/crash_gen.py", "libs/mojangapi.py", 
                "libs/cryptography_system/system.py"]
FOLDERS_TO_CHECK = ["libs", "libs/cryptography_system", "crash_reports", "logs", "plugins", "utils", "worlds"]

state = "_DEFAULT"
missing_files = []
missing_folders = []
i = 0
j = 0

def install():
    for d in missing_folders:
        os.mkdir(d)
    for f in missing_files:
        with open(f, "w") as f:
            f.write(dico[f])

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
    resp = input("Do you want to make this operation automatically ? You will not need to restart this script once it will be done. (o/n)\n\n-> ")
    if resp.lower() == "o":
        print("Installing...")
        install()
        print("Done.")
    else:
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

exec(compile(code, 'main.py', 'exec'), {"__name__":"__start__"})""".format(dico)

with open("start.py", "w") as f:
    f.write(template)