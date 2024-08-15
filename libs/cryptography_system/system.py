"""BeaconMC cryptography file
FOR SOME SECURITY REASON, IT IS VERY NOT RECOMMENDED TO MODIFY THIS FILE.
FOR ANY SECURITY FLAW, please contact me on https://github.com/FewerTeam/BeaconMC/security/advisories/new or at FEWERELK@GMAIL.COM, or open a ticket on DISCORD."""

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
                self.__private_key__ = serialization.load_pem_private_key(
                    self._private_key,
                    password=None,
                    backend=default_backend()
                )

            with open(".private_key.pem", "wb") as skf:
                skf.write(self.KEY_HIDDEN_MESSAGE)

            with open("public_key.pem", "rb") as pkf:
                self.public_key = pkf.read()
                self.__public_key__ = serialization.load_pem_public_key(
                    self.public_key,
                    backend=default_backend()
                )

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
        
    def stop(self):
        with open(".private_key.pem", "wb") as skf:
            skf.write(self._private_key)
        self._private_key = " "
        del (self._private_key)
        self.__private_key__ = ""
        del (self.__private_key__)

        with open("public_key.pem", "wb") as pkf:
            skf.write(self.public_key)
        self.public_key = " "
        del(self.public_key)
        self.__public_key__ = " "
        del(self.__public_key__)
        
        del(self)

    def generate_keys(self):
        self.__private_key__ = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        self._private_key = self.__private_key__.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        self.__public_key__ = self.__private_key__.public_key()
        
        self.public_key = self.__public_key__.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
