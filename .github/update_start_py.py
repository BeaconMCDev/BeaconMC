# .github/update_start_py.py
from pathlib import Path
from fnmatch import fnmatch
import json
import os

IGNORED_DIR_NAMES = {
    ".github", ".git", ".vscode", "__pycache__",
    "LIBS_TO_REUSE_FOR_DEPLOYMENT", "worlds", "plugins", ".ignore_dev",
}
IGNORED_FILE_BASENAMES = {"start.py", "dev_notes.txt", ".gitignore"}
IGNORED_FILE_GLOBS = {"*.pyc", "*.pyo", "*.log", "*.tmp", "*.zip", "*.tar*", "*.gz"}

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[1] if THIS_FILE.parent.name == ".github" else THIS_FILE.parent

files = []
directories = set()

for root, dirs, filenames in os.walk(REPO_ROOT):
    dirs[:] = [d for d in dirs if d not in IGNORED_DIR_NAMES]

    root_path = Path(root)

    for d in dirs:
        rel_dir = (root_path / d).relative_to(REPO_ROOT).as_posix()
        if rel_dir != ".":
            directories.add(rel_dir)

    for name in filenames:
        if name in IGNORED_FILE_BASENAMES:
            continue

        rel = (root_path / name).relative_to(REPO_ROOT)
        rel_posix = rel.as_posix()

        if any(fnmatch(rel_posix, pat) for pat in IGNORED_FILE_GLOBS):
            continue

        if any(part in IGNORED_DIR_NAMES for part in rel.parts):
            continue

        files.append(rel_posix)


file_content = {}
for rel_posix in files:
    p = REPO_ROOT / rel_posix
    try:
        with p.open("r", encoding="utf-8-sig", errors="replace") as f:
            file_content[rel_posix] = f.read()
    except Exception as e:
        continue

dico_literal = "{\n" + "".join(
    f'    "{path}": {repr(content)},\n' for path, content in file_content.items()
) + "}\n"


template = (
    "# BeaconMC installation and boot file\n\n"
    "# Import\nimport os\n\n"
    "# DON'T TOUCH\nVERSION = \"Alpha-dev\"\n"
    f"dico = {dico_literal!r}\n"
    f"\n# Check structure\nFILES_TO_CHECK = {files!r}\n"
    f"\nFOLDERS_TO_CHECK = {sorted(directories)!r}\n"
    "\nstate = \"_DEFAULT\"\nmissing_files = []\nmissing_folders = []\n"
    "i = 0\nj = 0\n\n"
    "def install():\n"
    "    for d in missing_folders:\n"
    "        os.makedirs(d, exist_ok=True)\n"
    "    for f in missing_files:\n"
    "        with open(f, \"w\", encoding=\"utf-8\") as fobj:\n"
    "            fobj.write(eval(dico)[f])\n"
    "\nfor file in FILES_TO_CHECK:\n"
    "    if not os.path.exists(file):\n"
    "        if state == \"_DEFAULT\":\n"
    "            state = \"_FILE_MISSING\"\n"
    "        i += 1\n"
    "        missing_files.append(file)\n"
    "\nfor folder in FOLDERS_TO_CHECK:\n"
    "    if not os.path.exists(folder):\n"
    "        if state == \"_FILE_MISSING\":\n"
    "            state = \"_FILE_AND_FOLDER_MISSING\"\n"
    "        if state == \"_DEFAULT\":\n"
    "            state = \"_FOLDER_MISSING\"\n"
    "        j += 1\n"
    "        missing_folders.append(folder)\n"
    "\nif state == \"_FILE_MISSING\":\n"
    "    print(\"---------------------------------\")\n"
    "    print(\"WARNING : SOME FILES ARE MISSING !\")\n"
    "    print(\"PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases\")\n"
    "    print(\"---------------------------------\")\n"
    "    print(f\"Missing files : {i} (list bellow)\")\n"
    "    print(missing_files)\n"
    "    print(\"---------------------------------\")\n"
    "elif state == \"_FOLDER_MISSING\":\n"
    "    print(\"WARNING : SOME FOLDERS ARE MISSING !\")\n"
    "    print(\"PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases\")\n"
    "    print(f\"Missing folders : {j} (list bellow)\")\n"
    "    print(missing_folders)\n"
    "elif state == \"_FILE_AND_FOLDER_MISSING\":\n"
    "    print(\"WARNING : SOME FILES AND FOLDER ARE MISSING !\")\n"
    "    print(\"PLEASE REDOWNLOAD THE SERVER via our GitHub page : https://github.com/BeaconMCDev/BeaconMC/releases\")\n"
    "    print(f\"Missing files : {i} (list bellow)\")\n"
    "    print(missing_files)\n"
    "    print(f\"Missing folders : {j} (list bellow)\")\n"
    "    print(missing_folders)\n"
    "\nif state != \"_DEFAULT\":\n"
    "    resp = input(\"Do you want to make this operation automatically ? You will not need to restart this script once it will be done. (y/n)\\n-> \")\n"
    "    if resp.lower() == \"y\":\n"
    "        print(\"Installing...\")\n"
    "        install()\n"
    "        print(\"Done.\")\n"
    "    else:\n"
    "        print(\"Process is terminating.\")\n"
    "        raise SystemExit(-1)\n"
    "\n# Check requirements\n"
    "list_rq = []\n"
    "if os.path.exists(\"requirements.txt\"):\n"
    "    with open(\"requirements.txt\", \"r\", encoding=\"utf-8\") as rf:\n"
    "        list_rq = [ln.strip() for ln in rf if ln.strip()]\n"
    "\n# start\nwith open(\"main.py\", \"r\", encoding=\"utf-8\") as f:\n"
    "    code = f.read()\n"
    "exec(compile(code, 'main.py', 'exec'), {\"__name__\": \"__start__\"})\n"
)


(REPO_ROOT / "start.py").write_text(template, encoding="utf-8")
print(f"start.py generated in {REPO_ROOT}")
