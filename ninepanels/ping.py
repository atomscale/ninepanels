from requests import get
from requests.exceptions import ConnectionError

from .core import config

try:
    resp = get(config.SERVER_ROOT)
    print(resp.status_code)
except ConnectionError as e:
    print(f"Server offline: {e}")
