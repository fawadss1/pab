"""
Package creation module for PAB
"""

import os
import tarfile
import tempfile
from datetime import datetime
from .exceptions import DeploymentError


class PackageManager:
    """Handles package creation for spider deployments"""

    @staticmethod
    def generate_version():
        """
        Generate a version string based on current timestamp

        Returns:
            str: Version string
        """
        return datetime.now().strftime('%Y%m%d%H%M%S')

    @staticmethod
    def create_deployment_package(target_dir):
        """
        Create a tar.gz package of the spider project

        Args:
            target_dir (str): Directory containing the spider project

        Returns:
            str: Path to the created package
        """
        if not os.path.exists(target_dir):
            raise DeploymentError(f"Target directory '{target_dir}' does not exist")

        # Create temporary file for the package
        temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
        temp_file.close()

        try:
            with tarfile.open(temp_file.name, 'w:gz') as tar:
                # Add all files in the target directory
                for root, dirs, files in os.walk(target_dir):
                    # Skip common directories that shouldn't be deployed
                    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']]

                    for file in files:
                        # Skip common files that shouldn't be deployed
                        if file.endswith(('.pyc', '.pyo', '.DS_Store')):
                            continue

                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, target_dir)
                        tar.add(file_path, arcname=arcname)

            return temp_file.name

        except Exception as e:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise DeploymentError(f"Failed to create deployment package: {str(e)}")
