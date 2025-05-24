import requests
import time
import random
from datetime import datetime
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import pytz
import os
import sys
import logging
from abis import WPHRS_ABI, SWAP_ROUTER_ABI, ERC20_ABI, POOL_ABI, LP_ROUTER_ABI
from colorama import Fore, Style, init

init()

class ConfigManager:
    
    BASE_URL = "https://api.pharosnetwork.xyz"
    RPC_URL = "https://testnet.dplabs-internal.com"
    
    TASK_ID = 103
    MAX_RETRIES = 5
    BACKOFF_FACTOR = 2
    DEADLINE_MINUTES = 10

    FEE = 500
    GAS_LIMITS = {
        'APPROVAL': 100000,
        'TRANSFER': 100000,
        'SWAP': 500000,
        'LIQUIDITY': 3000000
    }
    GAS_MULTIPLIER = 1.2
    FALLBACK_GAS_PRICE = 20000000000
    
    TOKEN_DECIMALS = 18
    SWAP_PERCENTAGE = 0.5  
    LIQUIDITY_PERCENTAGE = 0.25  
    SEND_PERCENTAGE = 0.1  
    
    TARGET_ADDRESS_COUNT = 95
    BASE_ADDRESS = '0xf8a1d4ff0f9b9af7ce58e1fc1833688f3bfd6115'
    
    WPHRS_CONTRACT_ADDRESS = Web3.to_checksum_address("0x76aaada469d23216be5f7c596fa25f282ff9b364")
    USDC_TOKEN_ADDRESS = Web3.to_checksum_address("0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37")
    USDT_TOKEN_ADDRESS = Web3.to_checksum_address("0xEd59De2D7ad9C043442e381231eE3646FC3C2939")
    SWAP_ROUTER_ADDRESS = Web3.to_checksum_address("0x1a4de519154ae51200b0ad7c90f7fac75547888a")
    LP_ROUTER_ADDRESS = Web3.to_checksum_address("0xf8a1d4ff0f9b9af7ce58e1fc1833688f3bfd6115")
    USDC_POOL_ADDRESS = Web3.to_checksum_address("0x0373a059321219745aee4fad8a942cf088be3d0e")
    USDT_POOL_ADDRESS = Web3.to_checksum_address("0x70118b6eec45329e0534d849bc3e588bb6752527")

    TASK_DESCRIPTIONS = {
        101: "Swap",
        102: "Add Liquidity",
        103: "Send to Friend"
    }
    
    PRIVATE_KEY_FILE = "PrivateKey.txt"
    
    HEADERS_TEMPLATE = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.5',
        'authorization': 'Bearer {}',
        'origin': 'https://testnet.pharosnetwork.xyz',
        'referer': 'https://testnet.pharosnetwork.xyz/',
        'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'content-length': '0'
    }
    
    TRANSACTION_SETTINGS = {
        'TRANSACTION_DELAY': 2,  
        'VERIFICATION_RETRIES': 10,
        'VERIFICATION_DELAY': 10  
    }
    
    LOGGING_CONFIG = {
        'TIMEZONE': 'Asia/Jakarta',
        'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
        'LOG_LEVEL': 'INFO'
    }
    
    ENDPOINTS = {
        'LOGIN': '/user/login',
        'PROFILE': '/user/profile',
        'TASKS': '/user/tasks',
        'VERIFY': '/task/verify',
        'SIGN_IN': '/sign/in'
    }
    
    EXPLORER_CONFIG = {
        'BASE_URL': 'https://api.socialscan.io/pharos-testnet/v1/explorer/transactions',
        'PAGE_SIZE': 200,
        'MAX_PAGES': 10
    }

    MIN_PHRS_BALANCE = 0.05
    
    TOKEN_COLORS = {
        'USDC': Fore.LIGHTRED_EX,
        'USDT': Fore.YELLOW,
        'PHRS': Fore.MAGENTA,
        'WPHRS': Fore.WHITE
    }
    
    TOKEN_PAIRS = [
        {
            'TOKEN_IN': 'PHRS',
            'TOKEN_OUT': 'USDC',
            'TOKEN_IN_ADDRESS': None,
            'TOKEN_OUT_ADDRESS': '0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37'
        },
        {
            'TOKEN_IN': 'USDC',
            'TOKEN_OUT': 'PHRS',
            'TOKEN_IN_ADDRESS': '0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37',
            'TOKEN_OUT_ADDRESS': None
        },
        {
            'TOKEN_IN': 'PHRS',
            'TOKEN_OUT': 'USDT',
            'TOKEN_IN_ADDRESS': None,
            'TOKEN_OUT_ADDRESS': '0xEd59De2D7ad9C043442e381231eE3646FC3C2939'
        },
        {
            'TOKEN_IN': 'USDT',
            'TOKEN_OUT': 'PHRS',
            'TOKEN_IN_ADDRESS': '0xEd59De2D7ad9C043442e381231eE3646FC3C2939',
            'TOKEN_OUT_ADDRESS': None
        },
        {
            'TOKEN_IN': 'WPHRS',
            'TOKEN_OUT': 'USDC',
            'TOKEN_IN_ADDRESS': '0x76aaada469d23216be5f7c596fa25f282ff9b364',
            'TOKEN_OUT_ADDRESS': '0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37'
        },
        {
            'TOKEN_IN': 'WPHRS',
            'TOKEN_OUT': 'USDT',
            'TOKEN_IN_ADDRESS': '0x76aaada469d23216be5f7c596fa25f282ff9b364',
            'TOKEN_OUT_ADDRESS': '0xEd59De2D7ad9C043442e381231eE3646FC3C2939'
        },
        {
            'TOKEN_IN': 'USDT',
            'TOKEN_OUT': 'WPHRS',
            'TOKEN_IN_ADDRESS': '0xEd59De2D7ad9C043442e381231eE3646FC3C2939',
            'TOKEN_OUT_ADDRESS': '0x76aaada469d23216be5f7c596fa25f282ff9b364'
        },
        {
            'TOKEN_IN': 'USDC',
            'TOKEN_OUT': 'WPHRS',
            'TOKEN_IN_ADDRESS': '0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37',
            'TOKEN_OUT_ADDRESS': '0x76aaada469d23216be5f7c596fa25f282ff9b364'
        }
    ]

class CustomFormatter(logging.Formatter):
    def format(self, record):
        jakarta_timezone = pytz.timezone(ConfigManager.LOGGING_CONFIG['TIMEZONE'])
        current_time = datetime.now(jakarta_timezone)
        time_str = current_time.strftime(ConfigManager.LOGGING_CONFIG['DATE_FORMAT'])
        
        msg = record.msg
        
        if record.levelno >= logging.ERROR:
            msg = f"{Fore.RED}{msg}{Style.RESET_ALL}"
        elif record.levelno >= logging.WARNING:
            msg = f"{Fore.YELLOW}{msg}{Style.RESET_ALL}"
        elif record.levelno >= logging.INFO:
            msg = f"{Fore.WHITE}{msg}{Style.RESET_ALL}"
        else:
            msg = f"{Fore.CYAN}{msg}{Style.RESET_ALL}"
        
        record.msg = f"{Fore.CYAN}[ {time_str} ]{Style.RESET_ALL}{Fore.WHITE} | {Style.RESET_ALL}{msg}"
        return super().format(record)

logger = logging.getLogger('PharosBot')
logger.setLevel(getattr(logging, ConfigManager.LOGGING_CONFIG['LOG_LEVEL']))

console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

def get_to_addresses(wallet_index=1):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://testnet.pharosscan.xyz',
        'priority': 'u=1, i',
        'referer': 'https://testnet.pharosscan.xyz/',
        'sec-ch-ua': '"Chromium";v="136", "Brave";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }

    base_url = ConfigManager.EXPLORER_CONFIG['BASE_URL']
    address = ConfigManager.BASE_ADDRESS
    target_count = ConfigManager.TARGET_ADDRESS_COUNT
    unique_addresses = set()
    attempt_count = 0
    
    total_pages = ConfigManager.EXPLORER_CONFIG['MAX_PAGES']
    page = (wallet_index % total_pages) + 1
    w3 = Web3()

    while len(unique_addresses) < target_count:
        attempt_count += 1
        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                params = {
                    'size': str(ConfigManager.EXPLORER_CONFIG['PAGE_SIZE']),
                    'page': str(page),
                    'address': address
                }
                response = requests.get(base_url, params=params, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    transactions = data.get("data", [])
                    if not transactions:
                        logger.warning(f"No transactions found on attempt {attempt_count} for page {page}")
                        page = (page % total_pages) + 1
                        continue

                    new_addresses = 0
                    for tx in transactions:
                        from_address = tx.get("from_address")
                        if from_address:
                            checksum_address = w3.to_checksum_address(from_address)
                            if checksum_address not in unique_addresses:
                                unique_addresses.add(checksum_address)
                                new_addresses += 1

                    # logger.info(f"Attempt {attempt_count}: Page {page}, Fetched {len(transactions)} transactions, {new_addresses} new addresses. Total unique: {len(unique_addresses)}/{target_count}")
                    
                    page = (page % total_pages) + 1
                    break
                else:
                    logger.warning(f"Attempt {attempt_count}, Retry {attempt}: Failed to fetch addresses. Status code: {response.status_code}")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Attempt {attempt_count}, Retry {attempt}: Error fetching addresses: {str(e)}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
        else:
            logger.error(f"Failed to fetch addresses after {ConfigManager.MAX_RETRIES} retries on attempt {attempt_count}")
            return list(unique_addresses)[:target_count]

        if len(unique_addresses) < target_count:
            time.sleep(10)

    return list(unique_addresses)[:target_count]

class Web3Manager:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(ConfigManager.RPC_URL))
        self.contract_cache = {}
        self._init_contracts()
        
    def _init_contracts(self):
        self.contract_cache['wphrs'] = self.web3.eth.contract(address=ConfigManager.WPHRS_CONTRACT_ADDRESS, abi=WPHRS_ABI)
        self.contract_cache['usdc'] = self.web3.eth.contract(address=ConfigManager.USDC_TOKEN_ADDRESS, abi=ERC20_ABI)
        self.contract_cache['usdt'] = self.web3.eth.contract(address=ConfigManager.USDT_TOKEN_ADDRESS, abi=ERC20_ABI)
        self.contract_cache['swapRouter'] = self.web3.eth.contract(address=ConfigManager.SWAP_ROUTER_ADDRESS, abi=SWAP_ROUTER_ABI)
        self.contract_cache['lpRouter'] = self.web3.eth.contract(address=ConfigManager.LP_ROUTER_ADDRESS, abi=LP_ROUTER_ABI)
        
    def get_contract(self, contract_type):
        return self.contract_cache.get(contract_type)
        
    def get_gas_price(self):
        try:
            base_gas = self.web3.eth.gas_price
            return int(base_gas * ConfigManager.GAS_MULTIPLIER)  
        except Exception:
            return ConfigManager.FALLBACK_GAS_PRICE
            
    def get_latest_nonce(self, wallet_address):
        try:
            return max(
                self.web3.eth.get_transaction_count(wallet_address, 'pending'),
                self.web3.eth.get_transaction_count(wallet_address, 'latest')
            )
        except Exception as e:
            logger.error(f"Error getting nonce for {wallet_address}: {e}")
            raise

    def get_token_balance(self, token_address, wallet_address):
        try:
            contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = contract.functions.balanceOf(wallet_address).call()
            return balance, balance / 10**ConfigManager.TOKEN_DECIMALS
        except Exception as e:
            logger.error(f"Error getting balance for {token_address}: {e}")
            raise

class TokenManager:
    def __init__(self, web3_manager):
        self.web3_manager = web3_manager
        self.web3 = web3_manager.web3

    def transfer_token(self, token_address, to_address, amount_wei, private_key, wallet_address):
        wallet_address = Web3.to_checksum_address(wallet_address)
        to_address = Web3.to_checksum_address(to_address)
        
        try:
            for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
                try:
                    nonce = self.web3_manager.get_latest_nonce(wallet_address)
                    gas_price = self.web3_manager.get_gas_price()
                    function_signature = "0xa9059cbb"
                    padded_address = to_address[2:].zfill(64)
                    padded_amount = hex(amount_wei)[2:].zfill(64)
                    data = function_signature + padded_address + padded_amount  
                                      
                    tx = {
                        'from': wallet_address,
                        'to': token_address,
                        'nonce': nonce,
                        'gas': ConfigManager.GAS_LIMITS['TRANSFER'],
                        'gasPrice': gas_price,
                        'chainId': self.web3.eth.chain_id,
                        'value': 0,
                        'data': data
                    }
                    
                    signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = f"0x{tx_hash.hex()}" if not tx_hash.hex().startswith("0x") else tx_hash.hex()
                    logger.info(f"Transfer TX: {tx_hash_hex}")
                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    if receipt['status'] == 0:
                        raise Exception("Transfer failed")
                    
                    return receipt, tx_hash_hex
                
                except Exception as e:
                    if 'nonce too low' in str(e).lower():
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    elif 'not in the chain' in str(e):
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    else:
                        raise Exception(f"Transfer error: {e}")
        
        except Exception as e:
            logger.error(f"Transfer error for {token_address}: {e}")
            raise

    def approve_token(self, token_address, spender_address, amount_wei, private_key, wallet_address):
        contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        wallet_address = Web3.to_checksum_address(wallet_address)
        
        try:
            if contract.functions.allowance(wallet_address, spender_address).call() >= amount_wei:
                return
            
            for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
                try:
                    nonce = self.web3_manager.get_latest_nonce(wallet_address)
                    gas_price = self.web3_manager.get_gas_price()
                    
                    tx = contract.functions.approve(spender_address, amount_wei).build_transaction({
                        'from': wallet_address,
                        'nonce': nonce,
                        'gas': ConfigManager.GAS_LIMITS['APPROVAL'],
                        'gasPrice': gas_price,
                        'chainId': self.web3.eth.chain_id
                    })
                    
                    signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = f"0x{tx_hash.hex()}" if not tx_hash.hex().startswith("0x") else tx_hash.hex()
                    logger.info(f"Approval TX: {tx_hash_hex}")
                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    if receipt['status'] == 0:
                        raise Exception("Approval failed")
                    
                    return receipt
                
                except Exception as e:
                    if 'nonce too low' in str(e).lower():
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    elif 'not in the chain' in str(e):
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    else:
                        raise Exception(f"Approval error: {e}")
        
        except Exception as e:
            logger.error(f"Approval error for {token_address}: {e}")
            raise

    def swap_tokens_exact_input(self, amount, token_in_symbol, token_out_symbol, private_key, wallet_address):
        swap_router = self.web3_manager.get_contract('swapRouter')
        
        try:
            token_in_address = None
            if token_in_symbol == 'PHRS':
                wrap_amount = int(amount * 10**ConfigManager.TOKEN_DECIMALS)
                receipt, _ = self.wrap_phrs(wrap_amount, private_key, wallet_address)
                if not receipt:
                    raise Exception("Failed to wrap PHRS")
                token_in_address = ConfigManager.WPHRS_CONTRACT_ADDRESS
            elif token_in_symbol == 'WPHRS':
                token_in_address = ConfigManager.WPHRS_CONTRACT_ADDRESS
            elif token_in_symbol == 'USDC':
                token_in_address = ConfigManager.USDC_TOKEN_ADDRESS
            elif token_in_symbol == 'USDT':
                token_in_address = ConfigManager.USDT_TOKEN_ADDRESS

            token_out_address = None
            if token_out_symbol == 'PHRS':
                token_out_address = ConfigManager.WPHRS_CONTRACT_ADDRESS
            elif token_out_symbol == 'WPHRS':
                token_out_address = ConfigManager.WPHRS_CONTRACT_ADDRESS
            elif token_out_symbol == 'USDC':
                token_out_address = ConfigManager.USDC_TOKEN_ADDRESS
            elif token_out_symbol == 'USDT':
                token_out_address = ConfigManager.USDT_TOKEN_ADDRESS

            amount_wei = int(amount * 10**ConfigManager.TOKEN_DECIMALS)
            balance_out_before_wei, _ = self.web3_manager.get_token_balance(token_out_address, wallet_address)
            balance_in_wei, balance_in = self.web3_manager.get_token_balance(token_in_address, wallet_address)
            
            if balance_in_wei < amount_wei:
                token_name = "WPHRS" if token_in_address == ConfigManager.WPHRS_CONTRACT_ADDRESS else "USDC" if token_in_address == ConfigManager.USDC_TOKEN_ADDRESS else "USDT"
                token_color = ConfigManager.TOKEN_COLORS.get(token_name, Fore.WHITE)
                raise ValueError(f"Insufficient balance: {balance_in} {token_color}{token_name}{Style.RESET_ALL}")
            
            self.approve_token(token_in_address, ConfigManager.SWAP_ROUTER_ADDRESS, amount_wei, private_key, wallet_address)
            
            deadline = int(time.time()) + (ConfigManager.DEADLINE_MINUTES * 60)
            params = (token_in_address, token_out_address, ConfigManager.FEE, wallet_address, amount_wei, 0, 0)
            
            exact_input_call = swap_router.functions.exactInputSingle(params).build_transaction({
                'from': wallet_address, 'value': 0
            })['data']
            
            for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
                try:
                    nonce = self.web3_manager.get_latest_nonce(wallet_address)
                    gas_price = self.web3_manager.get_gas_price()
                    
                    multicall_tx = swap_router.functions.multicall(deadline, [exact_input_call]).build_transaction({
                        'from': wallet_address,
                        'nonce': nonce,
                        'gas': ConfigManager.GAS_LIMITS['SWAP'],
                        'gasPrice': gas_price,
                        'chainId': self.web3.eth.chain_id
                    })
                    
                    signed_tx = self.web3.eth.account.sign_transaction(multicall_tx, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = f"0x{tx_hash.hex()}" if not tx_hash.hex().startswith("0x") else tx_hash.hex()
                    logger.info(f"Swap TX Sent -> TX Hash: {tx_hash_hex}")
                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    if receipt['status'] == 0:
                        raise Exception(f"Swap reverted: {receipt}")
                    
                    balance_out_after_wei, balance_out_after = self.web3_manager.get_token_balance(token_out_address, wallet_address)
                    output_amount = balance_out_after - (balance_out_before_wei / 10**ConfigManager.TOKEN_DECIMALS)
                    return tx_hash_hex, output_amount, balance_out_after
                
                except Exception as e:
                    if attempt < ConfigManager.MAX_RETRIES:
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                    else:
                        raise Exception(f"Swap failed after {ConfigManager.MAX_RETRIES} attempts: {e}")
        
        except Exception as e:
            logger.error(f"Swap error: {e}")
            raise

    def wrap_phrs(self, amount_wei, private_key, wallet_address):
        try:
            wallet_address = Web3.to_checksum_address(wallet_address)
            
            for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
                try:
                    nonce = self.web3_manager.get_latest_nonce(wallet_address)
                    gas_price = self.web3_manager.get_gas_price()
                    
                    tx = {
                        'from': wallet_address,
                        'to': ConfigManager.WPHRS_CONTRACT_ADDRESS,
                        'nonce': nonce,
                        'gas': ConfigManager.GAS_LIMITS['TRANSFER'],
                        'gasPrice': gas_price,
                        'chainId': self.web3.eth.chain_id,
                        'value': amount_wei,
                        'data': '0xd0e30db0'
                    }
                    
                    signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    tx_hash_hex = f"0x{tx_hash.hex()}" if not tx_hash.hex().startswith("0x") else tx_hash.hex()
                    logger.info(f"Wrap PHRS TX: {tx_hash_hex}")
                    
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    if receipt['status'] == 0:
                        raise Exception("Wrap failed")
                    
                    return receipt, tx_hash_hex
                
                except Exception as e:
                    if 'nonce too low' in str(e).lower():
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    elif 'not in the chain' in str(e):
                        time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
                        continue
                    else:
                        raise Exception(f"Wrap error: {e}")
        
        except Exception as e:
            logger.error(f"Wrap error: {e}")
            raise

    def perform_random_swap(self, private_key, wallet_address):
        try:
            phrs_balance_wei = self.web3.eth.get_balance(wallet_address)
            wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, wallet_address)
            usdc_balance_wei, usdc_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, wallet_address)
            usdt_balance_wei, usdt_balance = self.web3_manager.get_token_balance(ConfigManager.USDT_TOKEN_ADDRESS, wallet_address)

            phrs_balance_eth = float(phrs_balance_wei) / 10**18

            available_pairs = []
            for pair_config in ConfigManager.TOKEN_PAIRS:
                token_in = pair_config['TOKEN_IN']
                
                if token_in == 'PHRS':
                    if phrs_balance_eth > (ConfigManager.MIN_PHRS_BALANCE + 0.1):
                        available_pairs.append(pair_config)
                elif token_in == 'WPHRS' and wphrs_balance > 0.000001:
                    available_pairs.append(pair_config)
                elif token_in == 'USDC' and usdc_balance > 0.000001:
                    available_pairs.append(pair_config)
                elif token_in == 'USDT' and usdt_balance > 0.000001:
                    available_pairs.append(pair_config)

            if not available_pairs:
                raise Exception("No available token pairs for swapping")

            selected_pair = random.choice(available_pairs)
            token_in_symbol = selected_pair['TOKEN_IN']
            token_out_symbol = selected_pair['TOKEN_OUT']

            amount_to_swap = 0
            if token_in_symbol == 'PHRS':
                available_phrs_to_swap = phrs_balance_eth - ConfigManager.MIN_PHRS_BALANCE
                amount_to_swap = available_phrs_to_swap * ConfigManager.SWAP_PERCENTAGE
            elif token_in_symbol == 'WPHRS':
                amount_to_swap = wphrs_balance * ConfigManager.SWAP_PERCENTAGE
            elif token_in_symbol == 'USDC':
                amount_to_swap = usdc_balance * ConfigManager.SWAP_PERCENTAGE
            elif token_in_symbol == 'USDT':
                amount_to_swap = usdt_balance * ConfigManager.SWAP_PERCENTAGE

            token_in_color = ConfigManager.TOKEN_COLORS.get(token_in_symbol, Fore.WHITE)
            token_out_color = ConfigManager.TOKEN_COLORS.get(token_out_symbol, Fore.WHITE)
            logger.info(f"Performing swap: {amount_to_swap:.6f}{Style.RESET_ALL} {token_in_color}{token_in_symbol}{Style.RESET_ALL} -> {token_out_color}{token_out_symbol}{Style.RESET_ALL}")
            return self.swap_tokens_exact_input(amount_to_swap, token_in_symbol, token_out_symbol, private_key, wallet_address)

        except Exception as e:
            logger.error(f"swap error: {e}")
            raise

    def swap_to_phrs(self, private_key, wallet_address):
        try:
            wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, wallet_address)
            usdc_balance_wei, usdc_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, wallet_address)
            usdt_balance_wei, usdt_balance = self.web3_manager.get_token_balance(ConfigManager.USDT_TOKEN_ADDRESS, wallet_address)

            if wphrs_balance > 0.000001:
                logger.info(f"Attempting to unwrap WPHRS to PHRS...")
                try:
                    unwrap_amount_wei = wphrs_balance_wei
                    tx_data = '0x2e1a7d4d' + hex(unwrap_amount_wei)[2:].zfill(64)
                    tx = {
                        'from': wallet_address,
                        'to': ConfigManager.WPHRS_CONTRACT_ADDRESS,
                        'nonce': self.web3_manager.get_latest_nonce(wallet_address),
                        'gas': ConfigManager.GAS_LIMITS['TRANSFER'],
                        'gasPrice': self.web3_manager.get_gas_price(),
                        'chainId': self.web3.eth.chain_id,
                        'value': 0,
                        'data': tx_data
                    }
                    signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                    if receipt['status'] == 1:
                        logger.info("Successfully unwrapped WPHRS to PHRS")
                        return True
                except Exception as e:
                    logger.error(f"Failed to unwrap WPHRS: {e}")

            if usdc_balance > 0.000001:
                logger.info(f"Attempting to swap USDC to PHRS...")
                try:
                    amount = usdc_balance * 0.9
                    tx_hash, _, _ = self.swap_tokens_exact_input(amount, 'USDC', 'PHRS', private_key, wallet_address)
                    if tx_hash:
                        logger.info("Successfully swapped USDC to PHRS")
                        return True
                except Exception as e:
                    logger.error(f"Failed to swap USDC to PHRS: {e}")

            if usdt_balance > 0.000001:
                logger.info(f"Attempting to swap USDT to PHRS...")
                try:
                    amount = usdt_balance * 0.9
                    tx_hash, _, _ = self.swap_tokens_exact_input(amount, 'USDT', 'PHRS', private_key, wallet_address)
                    if tx_hash:
                        logger.info("Successfully swapped USDT to PHRS")
                        return True
                except Exception as e:
                    logger.error(f"Failed to swap USDT to PHRS: {e}")

            return False
        except Exception as e:
            logger.error(f"Error in swap_to_phrs: {e}")
            return False

class LiquidityManager:
    def __init__(self, web3_manager, token_manager):
        self.web3_manager = web3_manager
        self.token_manager = token_manager
        self.web3 = web3_manager.web3

    def add_liquidity(self, private_key, wallet_address, pool_address, token0_amount_wei, token1_amount_wei):
        try:
            pool_contract = self.web3.eth.contract(address=pool_address, abi=POOL_ABI)
            token0_address = pool_contract.functions.token0().call()
            token1_address = pool_contract.functions.token1().call()
            fee = pool_contract.functions.fee().call()
            
            logger.info(f"Pool Info: {token0_address} / {token1_address}")
            
            self.token_manager.approve_token(token0_address, ConfigManager.LP_ROUTER_ADDRESS, token0_amount_wei, private_key, wallet_address)
            self.token_manager.approve_token(token1_address, ConfigManager.LP_ROUTER_ADDRESS, token1_amount_wei, private_key, wallet_address)
            
            lp_router = self.web3_manager.get_contract('lpRouter')
            
            deadline = int(time.time()) + (ConfigManager.DEADLINE_MINUTES * 60)
            params = (
                token0_address,
                token1_address,
                fee,
                -887270,
                887270,
                token0_amount_wei,
                token1_amount_wei,
                0,
                0,
                wallet_address,
                deadline
            )
            
            gas_price = self.web3_manager.get_gas_price()
            gas_limit = ConfigManager.GAS_LIMITS['LIQUIDITY']
            try:
                estimated_gas = lp_router.functions.mint(params).estimate_gas({'from': wallet_address})
                gas_limit = int(estimated_gas * 1.5)
            except Exception as e:
                logger.warning(f"Gas estimation failed, using default: {e}")
            
            mint_tx = lp_router.functions.mint(params).build_transaction({
                'from': wallet_address,
                'nonce': self.web3_manager.get_latest_nonce(wallet_address),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'chainId': self.web3.eth.chain_id,
                'value': 0
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(mint_tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = f"0x{tx_hash.hex()}" if not tx_hash.hex().startswith("0x") else tx_hash.hex()
            
            logger.info(f"Add Liquidity TX Hash -> {tx_hash_hex}")
            
            try:
                logger.info(f"Waiting for transaction receipt...")
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                
                if tx_receipt['status'] == 1:
                    logger.info(f"Successfully added liquidity!")
                    return tx_receipt, tx_hash_hex
                else:
                    raise Exception(f"Transaction failed (status 0)")
            except Exception as e:
                logger.error(f"Transaction failed or timed out: {e}")
                return None, None
            
        except Exception as e:
            logger.error(f"Failed to add liquidity: {str(e)}")
            return None, None

class TaskManager:
    def __init__(self):
        self.headers = ConfigManager.HEADERS_TEMPLATE.copy()

    def get_profile_info(self, address, jwt_token):
        url = f"{ConfigManager.BASE_URL}{ConfigManager.ENDPOINTS['PROFILE']}?address={address}"
        headers = self.headers.copy()
        headers['authorization'] = f"Bearer {jwt_token}"

        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    if data.get("code") == 0:
                        user_info = data.get("data", {}).get("user_info", {})
                        total_points = user_info.get("TotalPoints", 0)
                        logger.info(f"Total Points: {total_points}")
                        return data["data"]["user_info"]
                    else:
                        raise Exception(f"Profile error: {data}")
                else:
                    logger.warning(f"Attempt {attempt}: Failed to get profile for {address[:10]}...")
            except Exception as e:
                logger.error(f"Attempt {attempt}: Profile fetch error for {address[:10]}...: {e}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
        return None

    def generate_signature(self, private_key, message="pharos"):
        web3 = Web3()
        msg = encode_defunct(text=message)
        signed_msg = web3.eth.account.sign_message(msg, private_key=private_key)
        signature = signed_msg.signature.hex()
        return signature if signature.startswith("0x") else f"0x{signature}"

    def get_jwt_token(self, address, signature):
        url = f"{ConfigManager.BASE_URL}{ConfigManager.ENDPOINTS['LOGIN']}?address={address}&signature={signature}"
        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                response = requests.post(url, headers=self.headers, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    if data.get("code") == 0:
                        return data["data"]["jwt"]
                    else:
                        raise Exception(f"JWT token error: {data}")
                else:
                    logger.warning(f"Attempt {attempt}: Received status code {response.status_code}")
            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
        return None

    def sign_in(self, address, jwt_token):
        url = f"{ConfigManager.BASE_URL}{ConfigManager.ENDPOINTS['SIGN_IN']}"
        params = {"address": address}
        headers = self.headers.copy()
        headers['authorization'] = f"Bearer {jwt_token}"

        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                response = requests.post(url, params=params, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    return response.json()
                else:
                    logger.warning(f"Attempt {attempt}: Sign-in failed for {address[:10]}... with status code {response.status_code}")
            except Exception as e:
                logger.error(f"Attempt {attempt}: Sign-in error for {address[:10]}...: {e}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)

        logger.error(f"Sign-in failed after {ConfigManager.MAX_RETRIES} attempts for {address[:10]}...")
        return None

    def get_tasks(self, address, jwt_token):
        url = f"{ConfigManager.BASE_URL}{ConfigManager.ENDPOINTS['TASKS']}?address={address}"
        headers = self.headers.copy()
        headers['authorization'] = f"Bearer {jwt_token}"

        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    if data.get("code") == 0:
                        tasks = data["data"]["user_tasks"]
                        if tasks:
                            logger.info(f"Current Task Status:")
                            for task_item in tasks:
                                task_id = task_item['TaskId']
                                if task_id in [101, 102, 103]:  
                                    complete_times = task_item['CompleteTimes']
                                    description = ConfigManager.TASK_DESCRIPTIONS.get(task_id, "Unknown Task")
                                    logger.info(f"Task {description} | Completed: {complete_times}x")
                        return tasks
                    else:
                        raise Exception(f"Task error: {data}")
                else:
                    logger.warning(f"Attempt {attempt}: Failed to get tasks for {address[:10]}...")
            except Exception as e:
                logger.error(f"Attempt {attempt}: Task fetch error for {address[:10]}...: {e}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)
        return None

    def verify_tx(self, address, jwt_token, tx_hash):
        url = f"{ConfigManager.BASE_URL}{ConfigManager.ENDPOINTS['VERIFY']}?address={address}&task_id={ConfigManager.TASK_ID}&tx_hash={tx_hash}"
        headers = self.headers.copy()
        headers['authorization'] = f"Bearer {jwt_token}"

        for attempt in range(1, ConfigManager.MAX_RETRIES + 1):
            try:
                response = requests.post(url, headers=headers, timeout=30)
                if response.status_code in (200, 201):
                    data = response.json()
                    verified = data.get("data", {}).get("verified", False)
                    
                    if verified:
                        logger.info(f"Verified")
                        return verified
                    
                    verify_retries = 0
                    while not verified and verify_retries < ConfigManager.TRANSACTION_SETTINGS['VERIFICATION_RETRIES']:
                        verify_retries += 1
                        time.sleep(ConfigManager.TRANSACTION_SETTINGS['VERIFICATION_DELAY'])
                        
                        retry_response = requests.post(url, headers=headers, timeout=30)
                        if retry_response.status_code in (200, 201):
                            retry_data = retry_response.json()
                            verified = retry_data.get("data", {}).get("verified", False)
                            if verified:
                                logger.info(f"Verified")
                                return verified
                    
                    return verified
                else:
                    logger.warning(f"Attempt {attempt}: Received status code {response.status_code}")
            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")

            time.sleep(ConfigManager.BACKOFF_FACTOR ** attempt)

        logger.error("Verification failed after retries")
        return False

class WalletManager:
    def __init__(self, web3_manager, token_manager, liquidity_manager, task_manager):
        self.web3_manager = web3_manager
        self.token_manager = token_manager
        self.liquidity_manager = liquidity_manager
        self.task_manager = task_manager
        self.web3 = web3_manager.web3
        self.transaction_counts = {
            'swap': 0,
            'liquidity': 0,
            'send': 0
        }

    def set_transaction_counts(self, counts):
        self.transaction_counts = counts

    def _process_wallet_operations(self, account, to_addresses, jwt_token=None):
        try:
            balance_wei = self.web3.eth.get_balance(account.address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            # logger.info(f"Balance: {balance_eth:.6f} {ConfigManager.TOKEN_COLORS['PHRS']}PHRS{Style.RESET_ALL}")
            
            if balance_eth < ConfigManager.MIN_PHRS_BALANCE:
                logger.warning(f"PHRS balance below minimum ({ConfigManager.MIN_PHRS_BALANCE}). Attempting recovery...")
                if self.token_manager.swap_to_phrs(account.key, account.address):
                    balance_wei = self.web3.eth.get_balance(account.address)
                    balance_eth = self.web3.from_wei(balance_wei, 'ether')
                    if balance_eth < ConfigManager.MIN_PHRS_BALANCE:
                        logger.warning(f"Recovery failed. PHRS balance still below minimum. Skipping operations.")
                        return
                    logger.info(f"Recovery successful. New PHRS balance: {balance_eth:.6f}")
                else:
                    logger.warning(f"Recovery failed. Skipping operations.")
                    return

            wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, account.address)
            usdc_balance_wei, usdc_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, account.address)
            usdt_balance_wei, usdt_balance = self.web3_manager.get_token_balance(ConfigManager.USDT_TOKEN_ADDRESS, account.address)
            
            # logger.info(f"WPHRS Balance: {wphrs_balance:.6f} {ConfigManager.TOKEN_COLORS['WPHRS']}WPHRS{Style.RESET_ALL}")
            # logger.info(f"USDC Balance: {usdc_balance:.6f} {ConfigManager.TOKEN_COLORS['USDC']}USDC{Style.RESET_ALL}")
            # logger.info(f"USDT Balance: {usdt_balance:.6f} {ConfigManager.TOKEN_COLORS['USDT']}USDT{Style.RESET_ALL}")
            
            logger.info(f"Balance Summary")
            logger.info(f"PHRS  : {balance_eth:.6f} PHRS{Style.RESET_ALL}")
            logger.info(f"wPHRS : {wphrs_balance:.6f} WPHRS{Style.RESET_ALL}")
            logger.info(f"USDC  : {usdc_balance:.6f} USDC{Style.RESET_ALL}")
            logger.info(f"USDT  : {usdt_balance:.6f} USDT{Style.RESET_ALL}")

            required_wphrs = 0
            if self.transaction_counts['swap'] > 0:
                required_wphrs += wphrs_balance * ConfigManager.SWAP_PERCENTAGE * self.transaction_counts['swap']
            if self.transaction_counts['liquidity'] > 0:
                required_wphrs += wphrs_balance * ConfigManager.LIQUIDITY_PERCENTAGE * self.transaction_counts['liquidity']
            if self.transaction_counts['send'] > 0:
                required_wphrs += wphrs_balance * ConfigManager.SEND_PERCENTAGE * self.transaction_counts['send']

            if wphrs_balance < required_wphrs and balance_eth > ConfigManager.MIN_PHRS_BALANCE + 0.1:
                wrap_amount_wei = int((balance_eth - ConfigManager.MIN_PHRS_BALANCE) * 0.5 * 10**18)
                logger.info(f"WPHRS balance insufficient. Wrapping {float(wrap_amount_wei) / 10**18:.6f} PHRS to WPHRS...")
                try:
                    receipt, tx_hash = self.token_manager.wrap_phrs(
                        wrap_amount_wei,
                        account.key,
                        account.address
                    )
                    if receipt:
                        logger.info("Successfully wrapped PHRS to WPHRS")
                except Exception as e:
                    logger.error(f"Failed to wrap PHRS: {e}")
            else:
                # logger.info("WPHRS balance sufficient or PHRS balance too low to wrap")
                pass

            wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, account.address)
            usdc_balance_wei, usdc_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, account.address)
            usdt_balance_wei, usdt_balance = self.web3_manager.get_token_balance(ConfigManager.USDT_TOKEN_ADDRESS, account.address)

            operations = []
            if wphrs_balance > 0.000001:
                operations.append('swap')
                if to_addresses:
                    operations.append('send')
            if usdc_balance > 0.000001:
                operations.append('liquidity')
            
            if not operations:
                logger.warning(f"No available operations to perform - insufficient balances")
                return

            # logger.info(f"Available operations: {', '.join(operations)}")
            logger.info(f"Transaction counts: SWAP : {self.transaction_counts['swap']} | LIQUIDITY : {self.transaction_counts['liquidity']} | SEND : {self.transaction_counts['send']}")
            
            if 'swap' in operations and self.transaction_counts['swap'] > 0:
                logger.info(f"Processing {self.transaction_counts['swap']} SWAP transactions...")
                for i in range(self.transaction_counts['swap']):
                    balance_wei = self.web3.eth.get_balance(account.address)
                    balance_eth = self.web3.from_wei(balance_wei, 'ether')
                    if balance_eth < ConfigManager.MIN_PHRS_BALANCE:
                        logger.warning(f"PHRS balance below minimum during swaps. Attempting recovery...")
                        if self.token_manager.swap_to_phrs(account.key, account.address):
                            balance_wei = self.web3.eth.get_balance(account.address)
                            balance_eth = self.web3.from_wei(balance_wei, 'ether')
                            if balance_eth < ConfigManager.MIN_PHRS_BALANCE:
                                logger.warning(f"Recovery failed. Stopping swaps.")
                                break
                            logger.info(f"Recovery successful. New PHRS balance: {balance_eth:.6f}")
                        else:
                            logger.warning(f"Recovery failed. Stopping swaps.")
                            break

                    logger.info(f"SWAP transaction {i+1}/{self.transaction_counts['swap']}")
                    try:
                        tx_hash, output_amount, balance_out_after = self.token_manager.perform_random_swap(
                            account.key,
                            account.address
                        )
                        logger.info(f"SWAP transaction {i+1}/{self.transaction_counts['swap']} completed")
                    except Exception as e:
                        logger.error(f"SWAP failed: {e}")
                        break
                        
                    time.sleep(ConfigManager.TRANSACTION_SETTINGS['TRANSACTION_DELAY'])

            if 'liquidity' in operations and self.transaction_counts['liquidity'] > 0:
                logger.info(f"Processing {self.transaction_counts['liquidity']} ADD LIQUIDITY transactions...")
                for i in range(self.transaction_counts['liquidity']):
                    if wphrs_balance <= 0.000001 or usdc_balance <= 0.000001:
                        logger.warning("Insufficient balance for adding liquidity")
                        break
                        
                    logger.info(f"ADD LIQUIDITY transaction {i+1}/{self.transaction_counts['liquidity']}")
                    try:
                        amount0_wei = int(wphrs_balance_wei * ConfigManager.LIQUIDITY_PERCENTAGE)
                        amount1_wei = int(usdc_balance_wei * ConfigManager.LIQUIDITY_PERCENTAGE)
                        receipt, tx_hash = self.liquidity_manager.add_liquidity(
                            account.key,
                            account.address,
                            ConfigManager.USDC_POOL_ADDRESS,
                            amount0_wei,
                            amount1_wei
                        )
                        if receipt:
                            logger.info(f"ADD LIQUIDITY transaction {i+1}/{self.transaction_counts['liquidity']} completed")
                    except Exception as e:
                        logger.error(f"ADD LIQUIDITY failed: {e}")
                        break
                        
                    wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, account.address)
                    usdc_balance_wei, usdc_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, account.address)
                    time.sleep(ConfigManager.TRANSACTION_SETTINGS['TRANSACTION_DELAY'])

            if 'send' in operations and self.transaction_counts['send'] > 0:
                logger.info(f"Processing {self.transaction_counts['send']} SEND transactions...")
                for i in range(self.transaction_counts['send']):
                    if wphrs_balance <= 0.000001 or not to_addresses:
                        logger.warning("Insufficient WPHRS balance or no more addresses to send to")
                        break
                        
                    to_address = random.choice(to_addresses)
                    to_addresses.remove(to_address)
                    amount_to_send = wphrs_balance * ConfigManager.SEND_PERCENTAGE
                    amount_to_send_wei = int(amount_to_send * 10**ConfigManager.TOKEN_DECIMALS)
                    logger.info(f"SEND transaction {i+1}/{self.transaction_counts['send']}: {amount_to_send:.6f} WPHRS to {to_address}")
                    
                    try:
                        receipt, tx_hash = self.token_manager.transfer_token(
                            ConfigManager.WPHRS_CONTRACT_ADDRESS,
                            to_address,
                            amount_to_send_wei,
                            account.key,
                            account.address
                        )
                        if receipt:
                            logger.info(f"SEND transaction {i+1}/{self.transaction_counts['send']} completed")
                            if jwt_token and ConfigManager.TASK_ID == 103:
                                self.task_manager.verify_tx(account.address, jwt_token, tx_hash)
                    except Exception as e:
                        logger.error(f"SEND failed: {e}")
                        break
                        
                    wphrs_balance_wei, wphrs_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, account.address)
                    time.sleep(ConfigManager.TRANSACTION_SETTINGS['TRANSACTION_DELAY'])

            phrs_final_balance_wei = self.web3.eth.get_balance(account.address)
            wphrs_final_balance_wei, wphrs_final_balance = self.web3_manager.get_token_balance(ConfigManager.WPHRS_CONTRACT_ADDRESS, account.address)
            usdc_final_balance_wei, usdc_final_balance = self.web3_manager.get_token_balance(ConfigManager.USDC_TOKEN_ADDRESS, account.address)
            usdt_final_balance_wei, usdt_final_balance = self.web3_manager.get_token_balance(ConfigManager.USDT_TOKEN_ADDRESS, account.address)
            
            logger.info(f"Final Balances:")
            logger.info(f"PHRS Balance: {self.web3.from_wei(phrs_final_balance_wei, 'ether'):.6f}")
            logger.info(f"WPHRS Balance: {wphrs_final_balance:.6f}")
            logger.info(f"USDC Balance: {usdc_final_balance:.6f}")
            logger.info(f"USDT Balance: {usdt_final_balance:.6f}")
            
        except Exception as e:
            logger.error(f"Error processing wallet operations: {e}")
            raise

    def process_wallet(self, wallet_index, private_key, total_wallets):
        try:
            account = Account.from_key(private_key)
            logger.info(f"Wallet {wallet_index}/{total_wallets}: {account.address}")

            signature = self.task_manager.generate_signature(private_key)
            jwt_token = self.task_manager.get_jwt_token(account.address, signature)
            if jwt_token:
                self.task_manager.get_profile_info(account.address, jwt_token)
                self.task_manager.get_tasks(account.address, jwt_token)
                
            to_addresses = get_to_addresses(wallet_index)
            if not to_addresses:
                logger.error(f"Failed to get target addresses")
                return

            self._process_wallet_operations(account, to_addresses, jwt_token)

        except Exception as e:
            logger.error(f"Wallet error: {e}")
            raise

class MainBot:
    def __init__(self):
        self.web3_manager = Web3Manager()
        self.token_manager = TokenManager(self.web3_manager)
        self.liquidity_manager = LiquidityManager(self.web3_manager, self.token_manager)
        self.task_manager = TaskManager()
        self.wallet_manager = WalletManager(
            self.web3_manager,
            self.token_manager,
            self.liquidity_manager,
            self.task_manager
        )
        self.transaction_counts = {
            'swap': 0,
            'liquidity': 0,
            'send': 0
        }

    def get_user_input(self):
        print(f"{Fore.CYAN}=== Transaction Configuration ==={Style.RESET_ALL}")
        while True:
            try:
                swap_count = int(input(f"{Fore.GREEN}SWAP count (0-100): {Style.RESET_ALL}"))
                if 0 <= swap_count <= 100:
                    break
                print(f"{Fore.RED}Enter 0-100{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid number{Style.RESET_ALL}")

        while True:
            try:
                liquidity_count = int(input(f"{Fore.GREEN}LIQUIDITY count (0-100): {Style.RESET_ALL}"))
                if 0 <= liquidity_count <= 100:
                    break
                print(f"{Fore.RED}Enter 0-100{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid number{Style.RESET_ALL}")

        while True:
            try:
                send_count = int(input(f"{Fore.GREEN}SEND count (0-100): {Style.RESET_ALL}"))
                if 0 <= send_count <= 100:
                    break
                print(f"{Fore.RED}Enter 0-100{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid number{Style.RESET_ALL}")

        self.transaction_counts = {
            'swap': swap_count,
            'liquidity': liquidity_count,
            'send': send_count
        }
        
        total_transactions = sum(self.transaction_counts.values())
        print(f"{Fore.CYAN}Total transactions to perform: {total_transactions}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}SWAP: {swap_count}{Style.RESET_ALL} | {Fore.GREEN}LIQUIDITY: {liquidity_count}{Style.RESET_ALL} | {Fore.GREEN}SEND: {send_count}{Style.RESET_ALL}")
        
        confirm = input(f"{Fore.YELLOW}Confirm these settings? (y/n): {Style.RESET_ALL}").lower()
        if confirm != 'y':
            print(f"{Fore.RED}Please restart the program to configure transactions again.{Style.RESET_ALL}")
            sys.exit(0)

    def run(self):
        try:
            self.clear_terminal()
            self.get_user_input()
            self.wallet_manager.set_transaction_counts(self.transaction_counts)
            self.process_wallets()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            sys.exit(1)
        
    def clear_terminal(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def process_wallets(self):
        try:
            with open(ConfigManager.PRIVATE_KEY_FILE) as f:
                private_keys = [line.strip() for line in f if line.strip()]

            total_wallets = len(private_keys)
            logger.info(f"Total Wallets: {total_wallets}")

            for wallet_index, private_key in enumerate(private_keys, start=1):
                try:
                    self.wallet_manager.process_wallet(wallet_index, private_key, total_wallets)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error processing wallet {wallet_index}: {str(e)}")
                    continue
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Error reading wallet file: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        if not os.path.isfile(ConfigManager.PRIVATE_KEY_FILE):
            logger.error(f"{ConfigManager.PRIVATE_KEY_FILE} is missing. Please ensure it exists with private keys.")
            sys.exit(1)

        bot = MainBot()
        bot.run()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user. Stopping process...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)