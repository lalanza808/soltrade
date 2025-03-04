import os
import json
import base58

from solders.keypair import Keypair
from solana.rpc.api import Client
from soltrade.log import log_general


class Config:
    def __init__(self, path):
        self.path = path
        self.api_key = None
        self.private_key = None
        self.custom_rpc_https = None
        self.usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        self.sol_mint = "So11111111111111111111111111111111111111112"
        self.other_mint = None
        self.other_mint_decimals = None
        self.other_mint_symbol = None
        self.trading_interval_seconds = None
        self.slippage = None  # bps
        self.computeUnitPriceMicroLamports = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.path):
            log_general.error(
                "Soltrade was unable to detect the JSON file. Are you sure config.json has not been renamed or removed?")
            exit(1)

        with open(self.path, 'r') as file:
            try:
                config_data = json.load(file)
                self.api_key = config_data["api_key"]
                self.private_key = config_data["private_key"]
                self.custom_rpc_https = config_data.get("custom_rpc_https") or "https://api.mainnet-beta.solana.com/"
                self.other_mint = config_data.get("other_mint", "")
                self.other_mint_decimals = 10**int(config_data.get("other_mint_decimals", ""))
                self.other_mint_symbol = config_data.get("other_mint_symbol", "")
                self.trading_interval_seconds = int(config_data.get("trading_interval_seconds", "60"))
                self.slippage = int(config_data.get("slippage", "50"))
                self.computeUnitPriceMicroLamports = int(config_data.get("computeUnitPriceMicroLamports", 20 * 14000))  # default fee of roughly $.04 today
            except json.JSONDecodeError as e:
                log_general.error(f"Error parsing JSON: {e}")
                exit(1)
            except KeyError as e:
                log_general.error(f"Missing configuration key: {e}")
                exit(1)

    @property
    def keypair(self):
        try:
            return Keypair.from_bytes(base58.b58decode(self.private_key))
        except Exception as e:
            log_general.error(f"Error decoding private key: {e}")
            exit(1)

    @property
    def public_address(self):
        return self.keypair.pubkey()

    @property
    def client(self):
        rpc_url = self.custom_rpc_https
        return Client(rpc_url)


_config_instance = None


def config(path=None):
    global _config_instance
    if _config_instance is None and path is not None:
        _config_instance = Config(path)
    return _config_instance
