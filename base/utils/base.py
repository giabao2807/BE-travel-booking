import string
import secrets


class Utils:
    @classmethod
    def gen_password(cls):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        return password
