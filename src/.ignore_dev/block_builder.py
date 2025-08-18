import json
import pprint

with open("blocks.json", "r") as items:
    data = json.load(items)
    data:dict

dict1 = {}
dict2 = {}

a = input("-> ")   # nvm just press "n"

for k, v in data.items():
    states = v["states"]
    name = k.split(":")[1]
    for i in states:
        try:
            if i["default"]:
                dict1[i["id"]] = name
                continue
        except KeyError:
            pass
        suffix = "["
        for prop, value in i["properties"].items():
            suffix += f"{prop}={value}, "
        suffix = suffix[:-2] + "]"
        dict1[i["id"]] = name + suffix

with open("output.py", "w") as f:
    f.write("dico = ")
    pprint.pprint(dict1, stream=f, width=120, compact=False)

if a == "y":
    for k, v in dict1.items():
        dict2[v] = k
    print(dict2)

else:
    print(dict1)
