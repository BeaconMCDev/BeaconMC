import pluginapi

main = None
name = None
#Il faudra que le loader mette les infos. Et qu'il retourne l'objet du srv et non pas main

main.log(f"Hi :D im running on a {pluginapi.core_get_version()} server !",3)

def load():
    main.log("Loading !", 0)

def on_server_start():
    main.log("The server is starting ! :-)", 0)

def on_player_join(player:str):
    main.log("A player is joining ! It is " + player, 0)

def on_player_leave(player):
    main.log("A player is leaving ! It is " + player, 0)
