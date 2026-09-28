import hashlib
import json


def build_package_bytes(package_data: dict) -> bytes:
    package_json = json.dumps(
        package_data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )
    return package_json.encode("utf-8")


def calculate_sha256(package_bytes: bytes) -> str:
    return hashlib.sha256(package_bytes).hexdigest()


def calculate_package_size(package_bytes: bytes) -> int:
    return len(package_bytes)
