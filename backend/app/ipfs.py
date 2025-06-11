# backend/app/ipfs.py

import requests
import json
from .config import settings

class IPFS_Client:
    def __init__(self):
        self.base_url = settings.IPFS_API_URL.rstrip("/")  # e.g. http://16.176.114.48:8000
        self.headers  = {"X-API-KEY": settings.IPFS_API_KEY}

    def upload_file(self, file_bytes: bytes, file_name: str) -> str:
        """multipart/form-data로 파일 업로드 → {"cid": "..."} 반환"""
        files = {
            "file": (file_name, file_bytes, "application/octet-stream")
        }
        resp = requests.post(
            f"{self.base_url}/upload",
            headers=self.headers,
            files=files
        )
        resp.raise_for_status()
        return resp.json()["cid"]

    def upload_text(self, text: str) -> str:
        """JSON body로 텍스트 업로드 → {"cid": "..."} 반환"""
        payload = {"text": text}
        resp = requests.post(
            f"{self.base_url}/upload_text",   # 만약 upload_text 경로가 다르면 변경
            headers={**self.headers, "Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        resp.raise_for_status()
        return resp.json()["cid"]

    def get_file(self, ipfs_hash: str) -> bytes:
        """{"cid":"..."} POST → binary content 반환"""
        payload = {"cid": ipfs_hash}
        resp = requests.post(
            f"{self.base_url}/download",
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )
        resp.raise_for_status()
        return resp.content

# 전역 인스턴스
ipfs_client = IPFS_Client()
