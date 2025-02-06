"""BeaconMC cryptography file
FOR SOME SECURITY REASON, IT IS VERY NOT RECOMMENDED TO MODIFY THIS FILE.
FOR ANY SECURITY FLAW, please contact me on https://github.com/FewerTeam/BeaconMC/security/advisories/new or at FEWERELK@GMAIL.COM, or open a ticket on DISCORD."""

# IMPORTS
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding
import os
import traceback

class CryptoSystem(object):
    KEY_HIDDEN_MESSAGE = b"403\nKEY HIDDEN FOR SECURITY REASONS. IT WILL BE WRITTEN HERE ON SERVER STOP (final action to prevent plugins accessing it)."
    PATH = "libs/cryptography_system/"

    def __init__(self, server):
        """Load public and private keys. Hide private key for security reason."""
        self.server = server
        try:
            with open(self.PATH + ".private_key.pem", "rb") as skf:
                self._private_key = skf.read()
                try:
                    self.__private_key__ = serialization.load_pem_private_key(
                        self._private_key,
                        password=None,
                        backend=default_backend()
                    )
                except Exception as e:
                    self.server.log(traceback.format_exc(), 2)
                    self.__private_key__ = None

            with open(self.PATH + ".private_key.pem", "wb") as skf:
                skf.write(self.KEY_HIDDEN_MESSAGE)

            with open(self.PATH + "public_key.pem", "rb") as pkf:
                self.public_key = pkf.read()
                try:
                    self.__public_key__ = serialization.load_pem_public_key(
                        self.public_key,
                        backend=default_backend()
                    )
                except Exception as e:
                    self.server.log(traceback.format_exc(), 2)
                    self.__public_key__ = None

            with open(self.PATH + "public_key.pem", "wb") as pkf:
                pkf.write(self.KEY_HIDDEN_MESSAGE)

            if self.null_keys():
                self.generate_keys()
        except FileNotFoundError:
            self.generate_keys()

    def null_keys(self) -> bool:
        """Check if keys exists or not (in project variables)."""
        null = (None, "", " ", "None", "none", "null", "Null")
        if self._private_key == self.KEY_HIDDEN_MESSAGE:
            # The initial key was not restored.
            return True
        if self._private_key in null:
            return True
        if self.public_key in null:
            return True
        return False

    def stop(self):
        with open(self.PATH + ".private_key.pem", "wb") as skf:
            skf.write(self._private_key)
        self._private_key = " "
        del (self._private_key)
        self.__private_key__ = ""
        del (self.__private_key__)

        with open(self.PATH + "public_key.pem", "wb") as pkf:
            pkf.write(self.public_key)
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

    def encode(self, data: bytes, secret: bytes = None) -> bytes:
        """
        Encode data using RSA (if secret is None) or AES (if secret is provided).

        :param data: Data to encode.
        :param secret: Shared key for AES encryption
        :return: Encoded data.
        """
        try:
            if secret is None:
                if not self.__public_key__:
                    raise ValueError("Public key not loaded.")
                # Chiffrement RSA avec OAEP padding
                encrypted = self.__public_key__.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                return encrypted
            else:
                # Chiffrement AES en mode CBC avec PKCS7 padding
                if len(secret) not in (16, 24, 32):
                    raise ValueError("Secret key must be 16, 24 or 32 octets lenth.")
                
                iv = os.urandom(16)  # IV de 16 octets pour AES
                cipher = Cipher(algorithms.AES(secret), modes.CBC(iv), backend=default_backend())
                encryptor = cipher.encryptor()

                padder = sym_padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()

                encrypted = encryptor.update(padded_data) + encryptor.finalize()
                return iv + encrypted  # Préfixer l'IV aux données chiffrées
        except Exception as e:
            self.server.log(f"Error while encoding : {str(e)}", 2)
            return b""

    def decode(self, data: bytes, secret: bytes = None) -> bytes:
        """
        Decode data using RSA (if secret is None) ou AES (if secret found).

        :param data: Data to decode.
        :param secret: Secret key for AES decoding.
        :return: Decoded data.
        """
        try:
            if secret is None:
                if not self.__private_key__:
                    raise ValueError("Private key not loaded.")
                decrypted = self.__private_key__.decrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                return decrypted
            else:
                if len(secret) not in (16, 24, 32):
                    raise ValueError("Private key must be 16, 24 or 32 octets lenth.")
                
                if len(data) < 16:
                    raise ValueError("Encoded data too short.")

                iv = data[:16]
                encrypted = data[16:]
                cipher = Cipher(algorithms.AES(secret), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()

                padded_data = decryptor.update(encrypted) + decryptor.finalize()

                unpadder = sym_padding.PKCS7(128).unpadder()
                decrypted = unpadder.update(padded_data) + unpadder.finalize()

                return decrypted
        except Exception as e:
            self.server.log(f"Error while decoding : {str(e)}", 2)
            return b""
