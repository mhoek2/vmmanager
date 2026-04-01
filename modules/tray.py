from typing import TYPE_CHECKING

import pystray
import os
import sys
from pystray import MenuItem as item
from PIL import Image, ImageDraw

if TYPE_CHECKING:
    from main import VMWareManager

class Tray:
    def __init__( self, context ) -> None:
        self.context    : 'VMWareManager' = context

        self.icon = pystray.Icon(
            "vm_manager",
            self.create_icon(),
            "VM Manager",
            menu=pystray.Menu(
                item("Open UI", self.open_page),
                item("Quit", self.quit_vmmanger)
            )
        )

    def resource_path( self, filename ):
        """Get path to resource, works for dev and PyInstaller exe"""
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, filename)
    
    def create_icon(self):
        image = Image.open(self.resource_path("static/icon.ico"))
        return image.resize((64, 64))

    def open_page( self, icon, item):
        import webbrowser
        webbrowser.open("http://localhost:5000")

    def quit_vmmanger( self, icon, item):
        self.icon.stop()
        import os
        os._exit(0)

    def run( self ):
        self.icon.run()