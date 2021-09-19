from colorama.ansi import Fore
from web3 import Web3
import web3
import requests
from summoner import Summoner 

class Transacter:
    """Class in charge of preparing and signing transactions"""

    # Configuration constants
    API_FTMSCAN_TOKEN = "VU7CVDPWW2GSFM7JWFCIP49AE9EPJVVSC4"

    # Contracts adresses
    contract_addresses = {
        "rarity": "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb",
        "summoner": "0xce761d788df608bd21bdd59d6f4b54b2e27f25bb", # Same as rarity but friendly name
        "gold": "0x2069B76Afe6b734Fb65D1d099E7ec64ee9CC76B2",
        "cellar": "0x2A0F1cB17680161cF255348dDFDeE94ea8Ca196A"
    }

    # Contracts adress checksums
    contract_checksums = {k: Web3.toChecksumAddress(v) for k, v in contract_addresses.items()}

    def __init__(self, address, private_key, txmode = "legacy"):
        self.address = address
        self.private_key = private_key
        self.txmode = txmode
        self.w3 =  Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
        self.nonce =  self.w3.eth.get_transaction_count(Web3.toChecksumAddress(self.address))
        # Prepare all contracts only once
        self.contracts = {cname: self.get_contract(cname) for cname in self.contract_addresses.keys()}
        self.session_cost = 0
        self.update_timestamp() # create self.timestamp
        self.pending_transactions = []


    def get_contract(self, contract_name):
        '''Get contract or raise a KeyError if contract isn't listed'''
        return self.w3.eth.contract(address = self.contract_checksums[contract_name], 
                                    abi = self.get_abi(self.contract_addresses[contract_name]))


    def get_abi(self, contract_address):
        '''Get abi from contract address'''
        abi_contract_url = "https://api.ftmscan.com/api?module=contract&action=getabi&address=" + \
            contract_address + "&apikey=" + self.API_FTMSCAN_TOKEN
        try:
            res = requests.get(abi_contract_url)
            res_json = res.json()
            abi = res_json["result"]
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        return abi

    def update_timestamp(self):
        self.timestamp = self.w3.eth.get_block('latest')["timestamp"]

    def get_gas_price(self):
        return self.w3.eth.gas_price / 1e18

    def sign_and_execute(self, w3fun, gas):
        """
        Sign and execute a web3 function call. 
        Returns a dict with {status, tx_hash, tx_receipt}.
        Status can be one of of "pending", "success" or "failure".
        For pending tx, tx_receipt will be `None`.
        """
        tx = w3fun.buildTransaction({
            'chainId': 250,
            'gas': gas,
            # TODO: gasprice is estimated automatically for now, will need to optimize it later
            'nonce': self.nonce})
        tx_signed = self.w3.eth.account.sign_transaction(tx, private_key = self.private_key)
        self.w3.eth.send_raw_transaction(tx_signed.rawTransaction)
        self.nonce = self.nonce + 1
        tx_hash = self.w3.toHex(self.w3.keccak(tx_signed.rawTransaction))
        
        current_gas_price = self.get_gas_price()
        estimated_cost = gas * current_gas_price
        print("Transaction sent, paying up to " + str(round(estimated_cost, 6)) + " FTM, id: " + tx_hash)
        
        if self.txmode == "batch":
            self.pending_transactions.append({"tx_hash": tx_hash, "gas_price": current_gas_price})
            return {"status": "pending", "hash": tx_hash, "receipt": None}
        else:
            # Check receipt status
            print("Waiting for receipt...")
            tx_receipt = self.wait_for_tx(tx_hash, gas_price_for_log = current_gas_price)
            tx_status = "success" if tx_receipt.status == 1 else "failure"
            return {"status": tx_status, "hash": tx_hash, "receipt": tx_receipt}


    def wait_for_tx(self, tx_hash, gas_price_for_log, wait_timeout = 360):
        # Wait for receipt
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, wait_timeout)
        except web3.exceptions.TransactionNotFound as e:
            print(Fore.RED + "Tx not found:" + str(e))
        except web3.exceptions.TimeExhausted as e:
            print(Fore.RED + "Tx may have failed:" + str(e))

        if tx_receipt.status == 1:
            actual_cost = tx_receipt.gasUsed * gas_price_for_log
            print(Fore.GREEN + "Tx success, actual cost " + str(round(actual_cost, 6)) + " FTM, id: " + str(tx_hash))
            self.session_cost += actual_cost
        else:
            print(Fore.RED + "Tx failed (status = " + str(tx_receipt.status) + ")")
        return tx_receipt

    def wait_for_pending_transations(self, wait_timeout = 360):
        receipts = []
        if len(self.pending_transactions) > 0:
            print("Waiting for " + str(len(self.pending_transactions)) + " tx receipts...")
            for tx in self.pending_transactions:
                tx_receipt = self.wait_for_tx(tx["tx_hash"], gas_price_for_log = tx["gas_price"])
                receipts.append(tx_receipt)

        # Reset pending tx and return all receipts
        self.pending_transactions = []
        return receipts

    def print_gas_price(self):
        max_gas_per_action = {
            "adventure": 70000,
            "level_up": 70000,
            "claim_gold": 120000,
            "cellar": 120000
        }
        print("Max cost per action:")
        for action in max_gas_per_action:
            max_cost = max_gas_per_action[action] * self.get_gas_price()
            print(action.ljust(10, ' ') + " => " + str(max_cost) + "FTM")

    def summon_from_class(self, summoner_class):
        """Summon a new summoner of the specified class ID or class name. 
           summoner_class can be either the ID or the class name. Returns the summoner ID"""
        try:
            class_id = int(summoner_class)
        except ValueError:
            try:
                class_id = Summoner.classes.index(summoner_class)
            except ValueError:
                print("Invalid class name or ID: aborting")
                return None 
        return self.summon(class_id)

    def summon(self, class_id):
        """Summon a new summoner of the specified class. Returns the summoner ID"""
        try:
            class_name = Summoner.classes[class_id]
        except IndexError:
            print("Invalid class id: aborting")
            return None 
        summon_fun = self.contracts["summoner"].functions.summon(class_id)
        tx_status = self.sign_and_execute(summon_fun, gas = 150000)
        details = self.get_details_from_summon_receipt(tx_status["receipt"])
        if details:
            print(Fore.GREEN + "Summoned new " + details["class_name"] + " (ID=" + str(details["token_id"]) + ")")
            return details["token_id"]
        else:
            print("Could not confirm summoner token_id")
            return None

    def get_details_from_summon_receipt(self, receipt):
        try:
            receipt_data = str(receipt.logs[1].data)
            receipt_class_id = int(receipt_data[(1+2):(64+2)], 16)
            receipt_token_id = int(receipt_data[(64+2):], 16)
            receipt_class_name = Summoner.classes[receipt_class_id]
            return {"token_id": receipt_token_id, "class_name": receipt_class_name}
        except:
            return None