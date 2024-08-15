"""BeaconMC cryptography file
FOR SOME SECURITY REASON, IT IS VERY NOT RECOMMENDED TO MODIFY THIS FILE.
FOR ANY SECURITY FLAW, please contact me on DISCORD or at FEWERELK@GMAIL.COM, NOT ON GITHUB."""

# IMPORTS
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class CryptoSystem(object):
    KEY_HIDDEN_MESSAGE = "403\nKEY HIDDEN FOR SECURITY REASONS. IT WILL BE WRITTEN HERE ON SERVER STOP (final action to prevent plugins access it)."
    
    def __init__(self, server):
        """Load public and private keys. Hide private key for security reason."""
        self.server = server
        try:
            with open(".private_key.pem", "rb") as skf:
                self._private_key = skf.read()
            with open(".private_key.pem", "wb") as skf:
                skf.write(self.KEY_HIDDEN_MESSAGE)
            with open("public_key.pem", "rb") as pkf:
                self.public_key = pkf.read()
            if self.null_key():
                self.generate_keys()
        except FileNotFoundError:
            self.generate_keys()

    def null_keys(self) -> bool:
        """Check if keys exists or not (in project variables)."""
        null = ("", " ", "None", "none", "null", "Null")
        if self._private_key == self.KEY_HIDDEN_MESSAGE:
            # The initial key was not restaured.
            return True
        if self._private_key in null:
            return True
        if self.public_key in null:
            return True
        return False

    def generate_keys(self):
        ...
