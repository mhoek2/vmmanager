from typing import TYPE_CHECKING
import json
import os
import sys

import subprocess

if TYPE_CHECKING:
    from main import VMWareManager

class VM_API:
    def __init__( self, context ) -> None:
        self.context    : 'VMWareManager' = context

        self.vm_dict = {}
        self.CONFIG_FILE = self.resource_path("config.json")
        self.VMS_FILE = self.resource_path("vms.json")

        self.vmrun = ""

        self.load_config()

    def resource_path( self, filename ):
        """Get path to resource, works for dev and PyInstaller exe"""
        if getattr(sys, 'frozen', False):  # running as compiled exe
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)


    def load_config( self ):
        if not os.path.exists( self.CONFIG_FILE ):
            return {}

        with open( self.CONFIG_FILE, "r" ) as f:
            data = json.load(f)

        self.vmrun = data.get("vmrun", "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe")

    def get_running_vms( self ):
        try:
            result = subprocess.run([
                self.vmrun, "list"], 
                capture_output=True, 
                text=True,
                creationflags=0x08000000 # No console
            )
            if result.returncode != 0:
                print("Error:", result.stderr)
                return False

            lines = result.stdout.splitlines()
            return set(lines[1:])

        except Exception as e:
           print(e)
           return False

    def load_vms( self ):
        if not os.path.exists( self.VMS_FILE ):
            return {}

        with open( self.VMS_FILE, "r" ) as f:
            data = json.load(f)

        return {vm["name"]: vm["path"] for vm in data.get("vms", [])}

    def save_vms( self, vm_dict ):
        data = {
            "vms": [
                {"name": name, "path": path}
                for name, path in vm_dict.items()
            ]
        }

        with open( self.VMS_FILE, "w" ) as f:
            json.dump(data, f, indent=2)

    def start_vm( self, path ):
        try:
            result = subprocess.run(
                [self.vmrun, "start", path], 
                capture_output=True, 
                text=True,
                creationflags=0x08000000 # No console                 
             )

            if result.returncode != 0:
                print("Error:", result)
                return False

            return True

        except Exception as e:
           print(e)
           return False

    def stop_vm_subprocesses( self, path : str, method : str ):
        return subprocess.run(
                [self.vmrun, "stop", path, method ], 
                capture_output=True, 
                text=True,
                timeout=15,
                creationflags=0x08000000 # No console
            )

    def stop_vm( self, path ):
        try:
            result = self.stop_vm_subprocesses( path, "soft" )

            if result.returncode != 0:
                print("Soft stop failed:", result.stderr)
        
            else:
                return True

        except subprocess.TimeoutExpired:
            print("soft stop timed out, try hard stop")

        # timeout.. go ahead and hard stop the vm
        try:
            print("go for hard stop")
            result = self.stop_vm_subprocesses( path, "hard" )

            if result.returncode != 0:
                print("Error:", result.stderr)
                return False

            return True

        except Exception as e:
           print(e)
           return False
