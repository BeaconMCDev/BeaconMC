#=========================
# BEACONMC 1.16.5
#=========================
# Mojang API

import requests
import json

class Accounts(object):
    def exists(self, username):
        """Check if the account exists"""
        try:
            response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx status codes)
            json_data = response.json()
            return True
        except Exception as e:
            return False

    def check(self, username):
        '''Check authenticity of an account'''
        try:
            with open("libs/requests/authcheck.json", "r") as f:
                import json
                data = json.loads(f.read())

            response = requests.post(url="https://authserver.mojang.com/authenticate", json=data)
            response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx status codes)
            print(json_data = response.json())
            
            return True
        except Exception as e:
            print(e)
            return False
        
if __name__ == "__main__":
    acc = Accounts()
    acc.check("EletrixTime")