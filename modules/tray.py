from typing import TYPE_CHECKING

import pystray
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

    def create_icon( self ):
        # simple black square icon
        image = Image.new('RGB', (64, 64), "black")
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill="white")
        return image

    def open_page( self, icon, item):
        import webbrowser
        webbrowser.open("http://localhost:5000")

    def quit_vmmanger( self, icon, item):
        self.icon.stop()
        import os
        os._exit(0)

    def run( self ):
        self.icon.run()