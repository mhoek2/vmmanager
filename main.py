import os
import threading
from flask import Flask, jsonify, request, render_template

from modules.vmapi import VM_API
from modules.tray import Tray

class VMWareManager:
    def __init__( self ) -> None:
        self.app = Flask(__name__)
        self.register_routes()

        self.vm_api : VM_API = VM_API( self )
        self.tray : Tray = Tray( self )

        print("VMWareManager initialized")

    # routes
    def register_routes( self ):

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/vms", methods=["GET"])
        def list_vms():
            vms = self.vm_api.load_vms()
            running = self.vm_api.get_running_vms()
            data = {
                'messages'  : [], 
                'list'      : [],
            }

            if running is False:
                data['messages'].append("vmware cannot be accessed, missing in system PATH?")

            for name, path in vms.items():
                if running:
                    status = "running" if path in running else "stopped"
                else:
                    status = "no connection"

                data['list'].append({"name": name, "status": status})
            
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
                return jsonify({"status": False, "message": "vmware cannot be accessed, missing in system PATH?"})

            return jsonify({"status": True})
        
        @self.app.route("/stop", methods=["POST"])
        def stop_vm():
            vms = self.vm_api.load_vms()
        
            name = request.json.get("name")
            path = vms.get( name )
        
            print(path)
            if not path:
                return jsonify({"error": "not found"}), 404
        
            result = self.vm_api.stop_vm( path )
            if not result:
                return jsonify({"status": False, "message": "vmware cannot be accessed, missing in system PATH?"})

            return jsonify({"status": True})

    # server
    def run_flask( self ):
        http_port = 5000
        print( f"Webserver starting on port {http_port}" )
        self.app.run( port = http_port )
 
    def run( self ) -> None: 
        flask_thread = threading.Thread(target=self.run_flask, daemon=True)
        flask_thread.start()

        self.tray.run()


if __name__ == "__main__":
    manager = VMWareManager()
    manager.run()

    #tray = Tray()
    #run_tray()

