# File: main.py
import os
import json
import subprocess
from pathlib import Path
from app_base import ApplicationBase
from loguru import logger

# logger.add("app.log", level="DEBUG")  # Logs to a file with debug level

class SyftboxMetadata(ApplicationBase):
    def __init__(self):
        self.app_name = "syftbox-metadata"
        super().__init__(os.environ.get("SYFTBOX_CLIENT_CONFIG_PATH"))
        self.my_user_id = self.client_config["email"]

    def generate_ecdsa_keys(self):
        """
        Generates ECDSA key pair if it doesn't already exist.
        """
        ecdsa_private_key_path = Path.home() / ".ssh" / "syftbox_ecdsa"
        ecdsa_public_key_path = Path(f"{ecdsa_private_key_path}.pub")

        if not ecdsa_private_key_path.exists() or not ecdsa_public_key_path.exists():
            logger.info("ECDSA keys not found. Generating new keys.")
            subprocess.run([
                "ssh-keygen", "-f", str(ecdsa_private_key_path), "-t", "ecdsa", "-b", "521", "-N", ""
            ], check=True)
            logger.info(f"ECDSA key pair generated at {ecdsa_private_key_path}")
        else:
            logger.info("ECDSA keys already exist.")

    def set_metadata_permissions(self):
        """
        Creates a _.syftperm file with all permissions set to my_user_id.
        """
        metadata_dir = self.public_dir(self.my_user_id) / "metadata"
        self.create_directory(metadata_dir)  # Ensure the directory exists
        self.set_permissions(metadata_dir, [self.my_user_id], [self.my_user_id], [self.my_user_id])
        logger.info(f"Permissions set for {metadata_dir}")

    def create_metadata_file(self):
        """
        Creates the metadata.json file with public key, email, and description.
        """
        # Define metadata.json path
        ecdsa_public_key_path = Path.home() / ".ssh" / "syftbox_ecdsa.pub"
        metadata_path = self.public_dir(self.my_user_id) / "metadata" / "metadata.json"
        
        # Read public key content
        with open(ecdsa_public_key_path, "r") as pubkey_file:
            public_key_content = pubkey_file.read().strip()

        # Prepare metadata
        metadata = {
            "public_key": public_key_content,
            "email": self.my_user_id,
            "description": "this datasite hosts some healthcare datasets"
        }

        # Write metadata.json
        self.create_file(metadata_path, json.dumps(metadata, indent=4))
        logger.info(f"Metadata file created at {metadata_path}")


if __name__ == "__main__":
    logger.info("-----------------------------")
    runner = SyftboxMetadata()
    
    # Generate ECDSA keys if needed
    runner.generate_ecdsa_keys()
    
    # Set metadata folder permissions
    runner.set_metadata_permissions()
    
    # Create metadata file
    runner.create_metadata_file()
    
    logger.info("Setup complete.")
