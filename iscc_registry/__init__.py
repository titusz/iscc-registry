from pydantic import BaseSettings
import appdirs

APP_NAME = "iscc-registry"
__version__ = "0.1.0"


# Ledger-ID Ethereum
LEDGER_ID_ETH = 0b01000000 .to_bytes(1, "big")


class Settings(BaseSettings):
    ipfs_address: str = "/ip4/127.0.0.1/tcp/5001/http"
    web3_address: str = "http://127.0.0.1:7545"
    contract_address: str = "0x031b3764C846a610BAbFede822a4b09972A8cff5"
    db_dir: str = appdirs.user_data_dir(appname=APP_NAME)


settings = Settings()
