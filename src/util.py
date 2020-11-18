from datetime import timezone, datetime
from typing import List


class BinanceAPIException(Exception):
    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


def datestr_to_timestamp(datestr: str) -> int:
    """
    Converts a given string of date to a binance timestamp

    The passed date string has have the following format: dd.mm.yyyy
    The created unix timestamp is in miliseconds and has timezone UTC
    """
    values: List[str] = datestr.split(".")
    day: int = int(values[0])
    month: int = int(values[1])
    year: int = int(values[2])

    # Validate time format
    if (day < 1 or day > 31) or (month < 1 or month > 12) or (year < 1000):
        raise Exception("Wrong time format")

    dt: datetime = datetime(year, month, day)
    ts: int = int(dt.timestamp())
    return ts
