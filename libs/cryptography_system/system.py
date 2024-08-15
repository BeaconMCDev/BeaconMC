"""BeaconMC cryptography file
FOR SOME SECURITY REASON, IT IS VERY NOT RECOMMENDED TO MODIFY THIS FILE.
FOR ANY SECURITY FLAW, please contact me on DISCORD or at FEWERELK@GMAIL.COM, NOT ON GITHUB."""

# IMPORTS
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class CryptoSystem(object):
    def __init__(self, server):
        """Load public and private keys. Hide private key for security reason."""
        self.server = server
        try:
            with open(".private_key.pem", "rb") as skf:
            self._PRIVATE_KEY = skf.read()
            with open(".private_key.pem", "wb" as skf:
                skf.write("403\nKEY HIDDEN FOR SECURITY REASONS. IT WILL BE WRITTEN HERE ON SERVER STOP (final action to prevent plugins access it).")
            with open("public_key.pem", "rb") as pkf:
                self.PUBLIC_KEY = pkf.read()
        except FileNotFoundError:
            ...
            # TODO: generate keys
