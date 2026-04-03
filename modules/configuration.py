from typing import TYPE_CHECKING

import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field

if TYPE_CHECKING:
    from main import VMWareManager

@dataclass(slots=True)
class Config:
    http_port               : int       = field( default=5000 )
    simulate                : bool      = field( default=False )
    vmrun                   : str       = field( default="C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe" )
    open_vmware_onstart     : bool      = field( default=False )

class Configuration:
    def __init__( self, context ) -> None:
        self.CONFIG_FILE = self.resource_path("config.json")

        self.var : Config = Config()
        self.data = asdict( self.var )

        # debug default config
        #self.print_config()

        self.load_config()

    def print_config( self ):
        json_config = json.dumps( self.data, indent=4 )
        print(json_config)
        
    def resource_path( self, filename ):
        """Get path to resource, works for dev and PyInstaller exe"""
        if getattr(sys, 'frozen', False):  # running as compiled exe
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, filename)

    def parse_config( self ):
        """Map this manually for now. use hasattr and setattr later"""
        self.var.http_port              = self.data.get("http_port",            self.var.http_port)
        self.var.simulate               = self.data.get("simulate",             self.var.simulate)
        self.var.vmrun                  = self.data.get("vmrun",                self.var.vmrun)
        self.var.open_vmware_onstart    = self.data.get("open_vmware_onstart",  self.var.open_vmware_onstart)

    def load_config( self ):
        if os.path.exists( self.CONFIG_FILE ):
            with open( self.CONFIG_FILE, "r" ) as f:
                self.data = json.load(f)

        else:
            print(f"{self.CONFIG_FILE} is not found, use defaults!")
            self.print_config()
        
        self.parse_config()

