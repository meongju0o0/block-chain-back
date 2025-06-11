import json
import os
from web3 import Web3
from solcx import install_solc, set_solc_version, compile_standard
from dotenv import load_dotenv

load_dotenv()

# ─── 경로 설정 ───────────────────────────────────────────────────────────────────────
SCRIPT_DIR    = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR      = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
CONTRACTS_DIR = os.path.join(ROOT_DIR, "contracts")
BACKEND_APP_DIR = os.path.join(ROOT_DIR, "backend", "app")
# ─────────────────────────────────────────────────────────────────────────────────────

RPC_URL        = os.getenv("RPC_URL")
PUBLIC_ADDRESS = os.getenv("PUBLIC_ADDRESS")
PRIVATE_KEY    = os.getenv("PRIVATE_KEY")
CHAIN_ID       = int(os.getenv("CHAIN_ID"))

# 솔리디티 소스 읽기
with open(os.path.join(CONTRACTS_DIR, "PaperChain.sol"), "r", encoding="utf-8") as f:
    paper_source = f.read()
with open(os.path.join(CONTRACTS_DIR, "CommentChain.sol"), "r", encoding="utf-8") as f:
    comment_source = f.read()

# 컴파일 설정
install_solc("0.8.17")
set_solc_version("0.8.17")
compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "PaperChain.sol": {"content": paper_source},
            "CommentChain.sol": {"content": comment_source},
        },
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.17",
)

paper_abi       = compiled["contracts"]["PaperChain.sol"]["PaperChain"]["abi"]
paper_bytecode  = compiled["contracts"]["PaperChain.sol"]["PaperChain"]["evm"]["bytecode"]["object"]
comment_abi     = compiled["contracts"]["CommentChain.sol"]["CommentChain"]["abi"]
comment_bytecode= compiled["contracts"]["CommentChain.sol"]["CommentChain"]["evm"]["bytecode"]["object"]

# Web3 세팅
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = PUBLIC_ADDRESS

# ─── EIP-1559 수수료 계산 헬퍼 ─────────────────────────────────────────────────────────
def make_fee_params(w3, tip_gwei: float = 1.0):
    max_priority = w3.to_wei(tip_gwei, "gwei")
    block = w3.eth.get_block("pending")
    base_fee = block.get("baseFeePerGas", 0)
    return {
        "maxFeePerGas": base_fee + max_priority,
        "maxPriorityFeePerGas": max_priority,
    }
# ─────────────────────────────────────────────────────────────────────────────────────

# ─── PaperChain 배포 ─────────────────────────────────────────────────────────────────
Paper = w3.eth.contract(abi=paper_abi, bytecode=paper_bytecode)
nonce = w3.eth.get_transaction_count(account)
fee_params = make_fee_params(w3, tip_gwei=1.0)
paper_tx = Paper.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "from": account,
    "nonce": nonce,
    "gas": 6_000_000,
    **fee_params,
})
signed_paper = w3.eth.account.sign_transaction(paper_tx, private_key=PRIVATE_KEY)
paper_hash  = w3.eth.send_raw_transaction(signed_paper.raw_transaction)
paper_rcpt  = w3.eth.wait_for_transaction_receipt(paper_hash)
print("PaperChain deployed to:", paper_rcpt.contractAddress)

# ─── CommentChain 배포 ────────────────────────────────────────────────────────────────
Comment = w3.eth.contract(abi=comment_abi, bytecode=comment_bytecode)
nonce += 1
fee_params = make_fee_params(w3, tip_gwei=1.0)
comment_tx = Comment.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "from": account,
    "nonce": nonce,
    "gas": 6_000_000,
    **fee_params,
})
signed_comment = w3.eth.account.sign_transaction(comment_tx, private_key=PRIVATE_KEY)
comment_hash  = w3.eth.send_raw_transaction(signed_comment.raw_transaction)
comment_rcpt  = w3.eth.wait_for_transaction_receipt(comment_hash)
print("CommentChain deployed to:", comment_rcpt.contractAddress)

# ─── 배포 정보 저장 ───────────────────────────────────────────────────────────────────
deployment_info = {
    "PaperChain": {
        "address": paper_rcpt.contractAddress,
        "abi": paper_abi,
    },
    "CommentChain": {
        "address": comment_rcpt.contractAddress,
        "abi": comment_abi,
    },
}
with open(os.path.join(BACKEND_APP_DIR, "deployment_info.json"), "w", encoding="utf-8") as f:
    json.dump(deployment_info, f, ensure_ascii=False, indent=2)
print("Saved deployment_info.json to", os.path.join(BACKEND_APP_DIR, "deployment_info.json"))
