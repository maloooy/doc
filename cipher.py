from cryptography.fernet import Fernet
import os

key_file_path = 'resources/secret.key'


def generate_and_save_key():
    key = Fernet.generate_key()
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)
    return key


def load_key():
    return open(key_file_path, 'rb').read()


if not os.path.exists(key_file_path):
    key = generate_and_save_key()
else:
    key = load_key()

cipher_suite = Fernet(key)


def encrypt(data):
    encrypted = cipher_suite.encrypt(data.encode())
    return encrypted.decode()


def decrypt(data):
    try:
        decrypted = cipher_suite.decrypt(data.encode()).decode()
        return decrypted
    except Exception as e:
        print(f"Failed to decrypt: {data}, error: {e}")
        raise