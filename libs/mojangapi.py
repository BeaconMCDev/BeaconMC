# =========================
# BEACONMC 1.19.4
# =========================
# Mojang API
# (C) BeaconMC Team

import requests
import json


class MinecraftAccountVerificationError(Exception):
    pass


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
                data = json.loads(f.read())

            response = requests.post(url="https://authserver.mojang.com/authenticate", json=data)
            response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx status codes)
            print(json_data=response.json())

            return True
        except Exception as e:
            print(e)
            return False

    def authenticate(self, username, uuid):
        try:
            response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            
            if response.status_code == 200:
                profile = response.json()

                if profile['id'] == uuid.replace('-', ''):
                    return (True, "")
                else:
                    return (False, f"UUID doesn't match. Receivt: {uuid}, expected: {profile['id']}.")
            else:
                return (False, f"This username doesn't exist ({response.status_code}).")

        except Exception as e:
            raise MinecraftAccountVerificationError from e


if __name__ == "__main__":
    acc = Accounts()
    acc.check("EletrixTime")
    