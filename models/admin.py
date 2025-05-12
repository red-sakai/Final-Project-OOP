from .database import Database

# parent class admin in order to access database
class Admin:
    def __init__(self, username: str, password: str, otp_authentication: bool):
        self.__username = username
        self.__password = password
        self.__otp_authentication = otp_authentication

    def login(self, user: str, passw: str) -> bool:
        return self.__username == user and self.__password == passw

    @staticmethod
    def access_database() -> 'Database':
        return Database()