import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_PATH = Path(__file__).resolve().parent

class Settings: 

    DB_USER : str = os.getenv("DB_USER")
    DB_PASSWORD : str = os.getenv("DB_PASSWORD")
    DB_HOST : str = os.getenv("DB_HOST")
    DB_PORT : str = os.getenv("DB_PORT")
    DB_NAME : str = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URL : str = (f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    IPFS_API_URL : str = os.getenv("IPFS_API_URL")
    IPFS_API_KEY : str = os.getenv("IPFS_API_KEY")

    RPC_URL: str = os.getenv("RPC_URL")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID"))
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY")
    PUBLIC_ADDRESS: str = os.getenv("PUBLIC_ADDRESS")

    DEPLOYMENT_INFO_PATH: Path = BASE_PATH / "deployment_info.json"

settings = Settings