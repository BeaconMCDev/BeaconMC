# BeaconMC installation and boot file

# Import
import os

# Check structure
if os.path.exists("config.json"):
    ...

# Check requirements
...

# install server if required
...

# start
with open ("main.py", "r") as f:
    code = f.read()

exec(code, __name__="__main__")