# parent class for parcel database
class Parcel:
    def __init__(self, parcel_number: str, qr_code: str, bar_code: str):
        self.__parcel_number = parcel_number
        self.__qr_code = qr_code
        self.__bar_code = bar_code

    @property
    def parcel_number(self) -> str:
        return self.__parcel_number

    @property
    def qr_code(self) -> str:
        return self.__qr_code

    @property
    def bar_code(self) -> str:
        return self.__bar_code