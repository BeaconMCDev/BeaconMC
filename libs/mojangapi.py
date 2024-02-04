#=========================
# BEACONMC 1.16.5
#=========================
# Mojang API

import requests
import json

class Accounts(object):
    def check(self, username):
        '''Check authenticity of an account'''
        try:
            response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx status codes)
            json_data = response.json()
            return True
        except Exception as e:
            return False