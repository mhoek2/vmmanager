from typing import TYPE_CHECKING
import json
import os
import re
import sys

import subprocess

if TYPE_CHECKING:
    from main import VMWareManager

class VM_API:
    def __init__( self, context ) -> None:
        self.context    : 'VMWareManager' = context
        self.config     = self.context.config

        self.vm_dict = {}
        self.VMS_FILE = self.resource_path("vms.json")

    def resource_path( self, filename ):
        """Get path to resource, works for dev and PyInstaller exe"""
        if getattr(sys, 'frozen', False):  # running as compiled exe
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)

    def get_running_vms( self ):
        try:
            result = subprocess.run([
                self.config.var.vmrun, "list"], 
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
           #print(e)
           return False

    def get_ip_address( self, path ):
        result = subprocess.run(
            [self.config.var.vmrun, "getGuestIPAddress", path ], 
            capture_output=True, 
            text=True,
            timeout=5,
            creationflags=0x08000000 # No console
        )

        output = result.stdout.lower()

        if "vmware tools" in output and "not running" in output:
            return "vmware tools missing"
        
        return result.stdout.strip()

    def load_inventory_vms( self ):
        """Try to load the inventory from VMmware"""
        vms = {}

        appdata = os.getenv( "APPDATA" )
        if not appdata:
            return vms

        inv_path = os.path.join( appdata, "VMware", "inventory.vmls" )

        if not os.path.exists( inv_path ):
            return vms

        with open( inv_path, "r", encoding="utf-8", errors="ignore" ) as f:
            content = f.read()

        # find all .vmx paths
        matches = re.findall( r'"(.*?\.vmx)"', content, re.IGNORECASE )

        normalizd_paths = set()

        for path in matches:
            path_n = os.path.normcase( os.path.normpath( path ) )

            if not os.path.exists( path ):
                continue

            # unique path
            if path_n in normalizd_paths:
                continue

            normalizd_paths.add( path_n )

            base_name = os.path.splitext(os.path.basename(path))[0]
            name = base_name
            counter = 1

            # unique name
            while name in vms:
                name = f"{base_name} ({counter})"
                counter += 1

            vms[name] = path

        return vms

    def load_vms( self ):
        """Load vms from local tracked JSON file"""
        if not os.path.exists( self.VMS_FILE ):
            return {}

        with open( self.VMS_FILE, "r" ) as f:
            data = json.load(f)

        return {vm["name"]: vm["path"] for vm in data.get("vms", [])}

    def save_vms( self, vm_dict ):
        """Save vms to local tracked JSON file"""
        data = {
            "vms": [
                {"name": name, "path": path}
                for name, path in vm_dict.items()
            ]
        }

        with open( self.VMS_FILE, "w" ) as f:
            json.dump(data, f, indent=2)

    def import_inventory( self ):
        """Try to merge VMware's invertory with local tracked JSON file"""
        auto = self.load_inventory_vms()
        local = self.load_vms()

        added = 0
        existing = 0

        for name, path in auto.items():
            if name not in local:
                local[name] = path
                added += 1
            else:
                existing += 1

        self.save_vms( local )

        return added, existing

    def start_vm( self, path ):
        try:
            run_cmd = [self.config.var.vmrun, "start", path]

            # open vmware when start is pressed
            if not self.config.var.open_vmware_onstart:
                run_cmd.append("nogui")

            result = subprocess.run(
                run_cmd, 
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
                [self.config.var.vmrun, "stop", path, method ], 
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
