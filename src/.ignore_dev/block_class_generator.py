import json
import pprint

class PoissonDAout(Exception):
    pass

raise PoissonDAout("Vous pensee vraiment que je vais push 22k+ fichiers ?")
with open("blocks.json", "r") as f:
    data = json.load(f)

for name, value in data.items():
    namespace, n = name.split(":")
    definition = value["definition"]
    defstr = ""
    for k, v in definition.items():
        defstr += f"{k} = {json.dumps(v)}"
        defstr += "\n    "

    classdata = f"""from block import Block
from ..location import Location
class {''.join(word.capitalize() for word in n.split('_'))}(Block):
    
    {defstr}
    PROPERTIES = {repr(value["properties"])}
    def __init__(self, location:Location, properties={{}}):
        super().__init__("{namespace}", "{n}", location, properties)"""

    with open(f"{n}.py", "w") as f:
        f.write(classdata)

print("Opt effectuée")
