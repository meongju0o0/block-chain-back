import json
from web3 import Web3
from .config import settings

class BlockChain_Client : 

    def __init__ (self) : 
        self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))

        self.account = settings.PUBLIC_ADDRESS
        self.private_key = settings.PRIVATE_KEY
        self.chain_id = settings.CHAIN_ID


        with open(settings.DEPLOYMENT_INFO_PATH, "r", encoding = "utf-8") as f :
            deployment = json.load(f)

        paper_info = deployment["PaperChain"]
        self.paper_contract = self.w3.eth.contract(
            address = Web3.to_checksum_address(paper_info["address"]),
            abi = paper_info["abi"]
        )

        comment_info = deployment["CommentChain"]
        self.comment_contract = self.w3.eth.contract(
            address = Web3.to_checksum_address(comment_info["address"]), 
            abi = comment_info["abi"]
        )
        
    def submit_paper (self, paper_id : int, submitter_wallet : str, ipfs_hash : str) -> str : 

        nonce = self.w3.eth.get_transaction_count(self.account)
        txn = self.paper_contract.functions.submitPaper(
            paper_id,
            Web3.to_checksum_address(submitter_wallet),
            ipfs_hash
        ).build_transaction({
            "chainId" : self.chain_id,
            "gas" : 200_000,
            "gasPrice" : self.w3.to_wei("2", "gwei"),
            "nonce" : nonce,
        })

        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key = self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()
    
    def submit_comment (self, comment_id : int, paper_id : int, reviewer_wallet : str, ipfs_hash : str) -> str :

        nonce = self.w3.eth.get_transaction_count(self.account)
        txn = self.comment_contract.functions.submitPaper(
            paper_id,
            Web3.to_checksum_address(reviewer_wallet),
            ipfs_hash
        ).build_transaction({
            "chainId" : self.chain_id,
            "gas" : 200_000,
            "gasPrice" : self.w3.to_wei("2", "gwei"),
            "nonce" : nonce,
        })

        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key = self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()
    
    
blockchain_client = BlockChain_Client()