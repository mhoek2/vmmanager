# VM Manager
A **Python** application serving a basic web-based page allowing to control the power-state of virtual machines hosted through **VMware Workstation**

## :fire: Installation (Windows)
1. Download the [Release](https://github.com/mhoek2/vmmanager/releases/download/latest/windows-package.zip) or [Latest Beta](https://github.com/mhoek2/vmmanager/releases/download/latest-beta/windows-package.zip) here.
1. Extract the contents and open the folder.
2. Open **config.json** and edit the path for **"vmrun"** entry to match with path to your VMware Workstation **vmrun.exe**.

## :fire: Usage (Windows)
- Launch **VM Manager** — opens a tab in your browser and appears in the system tray  
- Open the **web UI**:
  - Opens when application is launched
  - Right-click the system tray icon → **Open UI**
  - Or go to http://localhost:5000  

- The **web UI** lists your **VMware Workstation** virtual machines  
  - Click **Import VMware** to auto-detect them  
  - Or manually add a `.vmx` path  

- The table refreshes automaticly

- VM Table contains:
  - **VM Name**
  - **Status** of the VM
  - **Start / Stop** button depending on current state
  - **IP Address** when available, display the optained guest IP
  - **Remove** only removes it from the list (not from disk)

## :gear: Configuration
The file **config.json** contains a few adjustable settings:

| Setting               | Value                                                                 | Description                                                               |
|----------------------|----------------------------------------------------------------------|-----------------------------------------------------------------------------|
| http_port            | 5000                                                                 | The port number used by the HTTP server                                     |
| http_use_socketio    | true                                                                 | Use Socket.IO synchronization reducing overhead, false = xhr polling        |
| simulate             | false                                                                | Adds demo vms to the list with randomized states                            |
| vmrun                | C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe           | Path to the VMware `vmrun` executable                                       |
| open_vmware_onstart  | false                                                                | Determines whether VMware opens  on startup                                 |


<img width="1920" height="1080" alt="preview" src="https://raw.githubusercontent.com/mhoek2/vmmanager/refs/heads/main/preview.png" />

## Development

1. Install ```python``` from [the website](https://www.python.org/downloads/)  
    ```*verified versions: python: 3.12.7, 3.13.2, pip: 24.3.1```
3. Use the terminal in vscode or your preferred cli
2. Clone repository
	```bash
	git clone https://github.com/mhoek2/vmmanager
    cd vmmanager
	```
2. Install requirements/dependencies
	```bash
	pip install -r requirements.txt
	```
3. Run
	```bash
	./main.py
	```

### Build locally
1. Build the executable using:
	```bash
	pyinstaller main.spec
	```
2. ```VM Manager.exe``` will be available in the ```dist``` subfolder