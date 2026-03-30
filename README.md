# VM Manager
A **Python** application serving a basic web-based page allowing to control the power-state of virtual machines hosted through **VMware Workstation**

## :fire: Installation (Windows)
1. Download the [Release](https://github.com/mhoek2/vmmanager/releases/download/latest/windows-package.zip) or [Latest Beta](https://github.com/mhoek2/vmmanager/releases/download/latest-beta/windows-package.zip) here.
1. Extract the contents and open the folder.
2. Open **config.json** and edit the path for **"vmrun"** entry to match with path to your VMware Workstation **vmrun.exe**.

## :fire: Usage (Windows)
- Launch **VM Manager** — opens in your browser and appears in the system tray  
- Open the UI:
  - Right-click the tray icon → **Open UI**
  - Or go to http://localhost:5000  

- The web UI lists your **VMware Workstation** virtual machines  
  - Click **Import VMware** to auto-detect them  
  - Or manually add a `.vmx` path  

- The table refreshes every 3 seconds  

- Per VM:
  - **Start / Stop** depending on state  
  - **Remove** only removes it from the list (not from disk)

<img width="1920" height="1080" alt="preview" src="https://raw.githubusercontent.com/mhoek2/vmmanager/refs/heads/main/preview.png" />