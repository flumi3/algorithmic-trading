import os
from pathlib import Path


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


class TerminalColors:
    """
    Colors for colored print outputs.
    Usage: print(OKCYAN + "Text that will be colored" + ENDC)
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_project_root() -> Path:
    """Returns the path of the project root"""
    return Path(__file__).parent.parent


def run_tests() -> None:
    tests_dir_path = str(Path(__file__).parent) + "/tests"
    os.system(f"pytest {tests_dir_path} -o cache_dir={tests_dir_path}/pytest_cache")
