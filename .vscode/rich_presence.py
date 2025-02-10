from pypresence import Presence
import time


client_id = '1338551378242699374'

# Connexion avec Discord
rpc = Presence(client_id)
rpc.connect()


rpc.update(
    state="Developping BeaconMC",
    details="A Minecraft server, in Python 3 !",
    buttons=[
        {"label": "Join our Discord", "url": "https://discord.gg/pxkT9dtuN8"},
        {"label": "See project on GitHub", "url": "https://github.com/BeaconMCDev/BeaconMC"}
    ]
)


print("Done...")
while True:
    time.sleep(15)
