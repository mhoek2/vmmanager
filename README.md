# VM Manager
A **Python** application serving a basic web-based page allowing to control the power-state of virtual machines hosted through **VMware Workstation**

## :fire: Installation (Windows)
1. Download the [Release or Beta](https://github.com/mhoek2/vmmanager/releases) here.
1. Extract the contents and open the folder.
2. Open **config.json** and edit the path for **"vmrun"** entry to match your VMware Workstation install directory.

## :fire: Usage (Windows)
1. Launching "VM Manager" will run the app in the background/system tray
2. In the system tray, right click on the "VM Manager" 
	a. Select **"Open UI"** from the context menu.
	b. Or navigate to [http://localhost:5000](http://localhost:5000) in a web-browser
4. The web-page shows a table listing virtual machines from **VMware Workstation**.
	a. NOTE: You have to **manually** add the **.VMX path** for each virtual machine. 
5. The web-page is updating the table periodicly (3 seconds)
6. Each virtual machine has a **"Start"** button, if it is running it is replaced with **"Stop"**
7. The "Remove" button only removes the virtual machine from the table, it will not destroy it.