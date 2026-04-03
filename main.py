import os
import threading
import socket
import time
import random
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit

from modules.configuration import Configuration
from modules.vmapi import VM_API
from modules.tray import Tray

class VMWareManager:
    def __init__( self ) -> None:
        # configurationn
        self.config : Configuration = Configuration( self )

        # flask instance
        self.app = Flask(__name__)

        # flask socketio instance
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode="threading",)
        self.socketio_interval_sec = 4 
        self.socketio_data = []

        # routes
        self.register_routes()

        # modules
        self.vm_api : VM_API = VM_API( self )
        self.tray : Tray = Tray( self )

        print("VMWareManager initialized")

    def random_ip( self ):
        return ".".join(str(random.randint(1, 255)) for _ in range(4))

    def get_vms( self ):
        vms = self.vm_api.load_vms()
        running = self.vm_api.get_running_vms()
        data = {
            'messages'  : [], 
            'list'      : []
        }

        if running is False:
            data['messages'].append("vmware cannot be accessed, missing in system PATH?")

        for name, path in vms.items():
            if running is not False:
                status = "aan" if path in running else "gestopt"

                if not os.path.exists( path ):
                    status = "vmx onbekend"

                # try to find the IP address:
                if path in running:
                    ip_address = self.vm_api.get_ip_address( path )
                else:
                    ip_address = "x"

            else:
                status = "vmware fout"
                ip_address = "x"

            data['list'].append({"name": name, "status": status, "ip_address": ip_address})
            
        # simulate telemetry data
        if self.config.var.simulate:
            statuses = ["aan", "gestopt", "fout"]

            for i in range(4):
                status = random.choice(statuses)

                ip_address = self.random_ip() if status == "aan" else "x"

                data['list'].append({
                    "name": f"VM {i}",
                    "status": status,
                    "ip_address": ip_address
                })

        return data

    # routes
    def register_routes( self ):

        @self.socketio.on("connect")
        def handle_connect():
            print("Client connected")

            # send initial data immediately
            emit("vms_update", self.get_vms())

        @self.app.route("/")
        def index():
            return render_template(
                "index.html",
                config=self.config.var
            )

        @self.app.route("/inventory", methods=["GET"])
        def inventory_vms():
            vms = self.vm_api.load_inventory_vms()
            running = self.vm_api.get_running_vms()

            data = {
                'messages'  : [], 
                'list'      : [],
            }

            if running is False:
                data['messages'].append("vmware cannot be accessed, missing in system PATH?")

            for name, path in vms.items():
                if running is not False:
                    status = "aan" if path in running else "gestopt"
                else:
                    status = "vmware fout"

                data['list'].append({"name": name, "status": status})

            return jsonify(data)


        @self.app.route("/import_vms", methods=["GET"])
        def import_vms():
            added, existing = self.vm_api.import_inventory()

            data = {
                'added'     : added, 
                'existing'  : existing,
                'status'    : True
            }

            return jsonify(data)

        @self.app.route("/vms", methods=["GET"])
        def list_vms():
            data = self.get_vms()

            return jsonify(data)


        #
        # VM operations
        #
        @self.app.route("/add", methods=["POST"])
        def add_vm():
            data = request.json
            name = data.get("name")
            path = data.get("path")
        
            vms = self.vm_api.load_vms()
        
            if name in vms:
                return jsonify({"error": "VM already exists"}), 400
        
            vms[name] = path
            self.vm_api.save_vms( vms )
        
            return jsonify({"status": "added"})

        @self.app.route("/remove", methods=["POST"])
        def remove_vm():
            name = request.json.get("name")
        
            vms = self.vm_api.load_vms()

            if name not in vms:
                return jsonify({"error": False}), 400
        
            del vms[name]
            self.vm_api.save_vms( vms )
        
            return jsonify({"status": True})

        @self.app.route("/start", methods=["POST"])
        def start_vm():
            vms = self.vm_api.load_vms()
        
            name = request.json.get("name")
            path = vms.get( name )
        
            if not path:
                return jsonify({"error": False}), 404
        
            result = self.vm_api.start_vm( path )

            if not result:
                return jsonify({"status": False, "message": "vmware [vmrun] cannot be accessed"})

            return jsonify({"status": True})
        
        @self.app.route("/stop", methods=["POST"])
        def stop_vm():
            vms = self.vm_api.load_vms()
        
            name = request.json.get("name")
            path = vms.get( name )
        
            if not path:
                return jsonify({"error": "not found"}), 404
        
            result = self.vm_api.stop_vm( path )
            if not result:
                return jsonify({"status": False, "message": "vmware [vmrun] cannot be accessed"})

            return jsonify({"status": True})

    # socket
    def socket_update_loop( self ):
        if not self.config.var.http_use_socketio:
            return

        while True:
            data = self.get_vms()

            if self.socketio_data != data:
                self.socketio.emit("vms_update", data)
                self.socketio_data = data

            time.sleep( self.socketio_interval_sec )

    # server
    def run_flask( self ):
        print( f"Webserver starting on port {self.config.var.http_port}" )
        self.app.run( port = self.config.var.http_port )        

    def is_flask_running( self ):
        try:
            with socket.create_connection(("127.0.0.1", self.config.var.http_port), timeout=2):
                return True
        except OSError:
            return False

    def open_browser( self ):
        import webbrowser

        webbrowser.open(f"http://localhost:{self.config.var.http_port}")

    def open_browser_when_flask_active( self ):
        while not self.is_flask_running():
            time.sleep(0.1)

        self.open_browser()

    def run( self ) -> None: 
        """Start flask and open in a browser, if flask is already running, only open the browser"""
        if self.is_flask_running():
            print(f"Already listening on port {self.config.var.http_port}, open browser only")
            self.open_browser()
            return

        # flask
        flask_thread = threading.Thread(target=self.run_flask, daemon=True)
        flask_thread.start()

        # socket
        threading.Thread(target=self.socket_update_loop, daemon=True).start()
 
        # open browser as soon as flask webserver is active
        threading.Thread(target=self.open_browser_when_flask_active).start()
        
        # add tray icon
        threading.Thread(target=self.tray.run, daemon=False).start()

        if self.config.var.http_use_socketio:
            self.socketio.run(
                self.app, 
                port=self.config.var.http_port, 
                host="127.0.0.1",           # allow 'unsafe' for local tray app
                allow_unsafe_werkzeug=True
            )

if __name__ == "__main__":
    manager = VMWareManager()
    manager.run()
    