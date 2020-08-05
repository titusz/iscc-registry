from os.path import join

from pydantic import BaseSettings
import appdirs

APP_NAME = "iscc-registry"
APP_DIR = appdirs.user_data_dir(appname=APP_NAME)
ENV_PATH = join(APP_DIR, ".env")
__version__ = "0.1.0"


# Ledger-ID Ethereum
LEDGER_ID_ETH = 0b01000000 .to_bytes(1, "big")


class Settings(BaseSettings):
    ipfs_address: str = "/ip4/127.0.0.1/tcp/5001/http"
    web3_address: str = "http://127.0.0.1:7545"
    contract_address: str = ""
    db_dir: str = APP_DIR


settings = Settings(_env_file=ENV_PATH)
