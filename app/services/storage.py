from pathlib import Path
import hashlib

STORAGE_DIR = Path("storage/packages")



class LocalStorage:

    def __init__(
        self,
        base_dir: Path = STORAGE_DIR,
        base_url: str = "/storage/packages"):  
        self.base_dir = base_dir
        self.base_url = base_url


    def save_package(self,
    package_bytes: bytes,
    state_code: str,
    vehicle_code: str,
    version: str,
    module_code: str | None = None,
    ) -> Path:
        package_path = self.get_package_path(
        state_code=state_code,
        vehicle_code=vehicle_code,
        version=version,
        module_code=module_code,
        )

        package_path.write_bytes(package_bytes)

        return package_path

    def get_package_url(self,state_code: str, vehicle_code: str, version: str,
                        module_code: str | None = None) -> str:
        if module_code:
            return (
                f"{self.base_url}/"
                f"{state_code}/"
                f"{vehicle_code}/"
                f"{module_code}/"
                f"{version}.json"
            )
        return f"{self.base_url}/{state_code}/{vehicle_code}/{version}.json"


    def get_file_integrity(self,package_path: Path) -> tuple[str, int]:
        package_bytes = package_path.read_bytes()

        checksum_sha256 = hashlib.sha256(package_bytes).hexdigest()
        package_size_bytes = len(package_bytes)

        return checksum_sha256, package_size_bytes
    
    def verify_file_integrity(
            self, package_path: Path,
            expected_checksum: str,
    ) -> bool:
        actual_checksum, _ = self.get_file_integrity(package_path)
        return actual_checksum == expected_checksum

    def get_package_path(
        self,
        state_code: str,
        vehicle_code: str,
        version: str,
        module_code: str | None = None,
        ) -> Path:
        if module_code:
            directory = (
                self.base_dir
                / state_code
                / vehicle_code
                / module_code
            )
        else:
            directory = self.base_dir / state_code / vehicle_code

        directory.mkdir(parents=True, exist_ok=True)

        return directory / f"{version}.json"


    def stage_package(self, package_bytes: bytes, state_code: str, vehicle_code: str, version: str,
                      module_code: str | None = None) -> Path:
        if module_code:
            stage_dir = (
            self.base_dir
            / "staging"
            / state_code
            / vehicle_code
            / module_code
        )
        else:
            stage_dir = (
            self.base_dir
            / "staging"
            / state_code
            / vehicle_code
        )
            
        stage_dir.mkdir(parents=True, exist_ok=True)

        stage_path = stage_dir / f"{version}.json"
        stage_path.write_bytes(package_bytes)

        return stage_path


    def activate_package(self, staged_path: Path, state_code: str, vehicle_code: str,
                         version: str, module_code: str | None = None,) -> Path:
        if module_code:
            active_dir = (
            self.base_dir
            / state_code
            / vehicle_code
            / module_code
        )
        else:
            active_dir = (
            self.base_dir
            / state_code
            / vehicle_code
        )
        active_dir.mkdir(parents=True, exist_ok=True)

        active_path = active_dir / f"{version}.json"
    
        staged_path.replace(active_path)
    
        return active_path

storage = LocalStorage()