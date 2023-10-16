import __main__

# Existing imports
from platform import python_version
import pkg_resources
import psutil
from fastapi import APIRouter
from xposer.core.context import Context
import os
import re

def get_root_package_version():
    root_package_name = __main__.__package__
    if root_package_name:
        try:
            return pkg_resources.get_distribution(root_package_name).version
        except pkg_resources.DistributionNotFound:
            pass

    # Fallback: Look for setup.py in the main script directory
    main_script_dir = os.path.dirname(os.path.abspath(__main__.__file__))
    setup_py_path = os.path.join(main_script_dir, 'setup.py')
    if os.path.exists(setup_py_path):
        with open(setup_py_path, 'r') as f:
            setup_content = f.read()
            version_match = re.search(r'version=["\']([^"\']+)["\']', setup_content)
            if version_match:
                return version_match.group(1)

    return "Not Applicable"


class XPDebugRouter:
    @staticmethod
    def getRoute(ctx: Context):
        router = APIRouter()

        @router.get("/debug")
        async def read_debug_info():
            # Existing code ...
            python_version_info = python_version()
            current_package_version = pkg_resources.get_distribution("xposer").version
            all_packages = {d.project_name: d.version for d in pkg_resources.working_set}
            memory_info = {
                "virtual_memory": psutil.virtual_memory()._asdict(),
                "swap_memory": psutil.swap_memory()._asdict(),
                }

            root_package_version = get_root_package_version()  # Get root package version

            return {
                "python_version": python_version_info,
                "root_package_version": root_package_version,  # Include root package version
                "xposer": current_package_version,
                "all_packages": all_packages,
                "memory_info": memory_info,
                "configuration": ctx.config.model_dump()
                }

        return router
