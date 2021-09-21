from solcx import compile_standard, install_solc
from web3 import Web3
import json

with open("./SimpleStorage.sol", "r") as file:
    contract_file = file.read()

install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourcemap"]
                },
            },
        },
    },
    solc_version="0.6.0",
)


with open("./compile_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
chainId = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

print(SimpleStorage)

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chainId, "from": my_address, "nonce": nonce}
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

store_tx = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chainId, "from": my_address, "nonce": nonce + 1}
)

store_tx_signed = w3.eth.account.sign_transaction(store_tx, private_key)

store_tx_hash = w3.eth.send_raw_transaction(store_tx_signed.rawTransaction)

store_tx_receipt = w3.eth.wait_for_transaction_receipt(store_tx_hash)

print(simple_storage.functions.retrieve().call())