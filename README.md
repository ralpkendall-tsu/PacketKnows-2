# PacketKnows Setup Guide

## Overview
PacketKnows is an innovative Dual Mode Learning Platform designed to transform networking education. Built with HTML, CSS, HTMX, JavaScript, Django Python, SQLite, and GNS3 simulation, it offers a responsive interface for immersive training and testing environments.

The platform supports CCNA preparation with interactive learning, real-world networking simulations, and real-time progress tracking. Rigorous testing with students and IT experts highlights its reliability, security, and usability, earning praise for its educational value and effectiveness.

**PacketKnows supports four types of users:**

**Admin**: Manages the platform and user accounts.

**Instructor**: Facilitates courses, and tracks student progress.

**Student**: Participates in instructor-led training and activities.

**Self-learner**: Engages in independent study and testing using platform resources.

---

## Table of Contents
1. [Project Details](#project-details)
2. [Setup Steps](#setup-steps)
    - [Install VirtualBox](#1-install-virtualbox)
    - [Create a Linux VM (Ubuntu)](#2-create-a-linux-vm-ubuntu)
    - [Install VS Code](#3-install-vscode)
    - [Install Git](#4-install-git)
    - [Clone the Source Code](#5-clone-the-source-code)
    - [Install GNS3 with IOU Support](#6-install-gns3-with-iou-support)
    - [Configure GNS3](#7-configure-gns3)
    - [Run the Django Server](#8-run-the-django-server)
3. [Admin Credentials](#admin-credentials)
4. [Troubleshooting](#troubleshooting)

---

## Project Details
- **Designed in:** Figma
- **Planning Tool:** Kanban Board
- **Languages Used:** Django Python, HTMX, SQLite
- **Applications Integrated:** GNS3

---

## Setup Steps

### 1. Install VirtualBox
Download and install VirtualBox from the [official website](https://www.virtualbox.org/).

---

### 2. Create a Linux VM (Ubuntu)
1. Open VirtualBox and create a new virtual machine.
2. Install Ubuntu on the VM.
3. Configure the network settings of the VM to use a Bridged Adapter to ensure proper connectivity.

---

### 3. Install VS Code
Inside the Ubuntu VM, install Visual Studio Code:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common apt-transport-https wget -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install code -y
```

---

### 4. Install Git
Install Git to manage the repository:
```bash
sudo apt install git -y
```

---

### 5. Clone the Source Code
Clone the project repository to your local machine:
```bash
git clone https://github.com/your-username/PacketKnows.git
cd PacketKnows
```

---

### 6. Install GNS3 with IOU Support
Download and install GNS3 with IOU support:
```bash
sudo add-apt-repository ppa:gns3/ppa
sudo apt update
sudo apt install gns3-gui gns3-server -y
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install gns3-iou
```

---

### 7. Configure GNS3

#### a. Setup Wizard
1. Open GNS3.
2. Choose **Run appliances on my local computer**.
3. Set the **Host Binding** to your local IP address (e.g., `192.168.100.107`).

#### b. Install Router
1. Go to **Preferences > Dynamips > IOS routers**.
2. Add an IOS router and configure the **WIC Modules**:
    - `WIC 0: WIC-2T`.

#### c. Install Switch
1. Go to **Preferences > IOS on UNIX > IOU Devices**.
2. Add the IOU switch image.

#### d. Add Projects
1. Extract the GNS3 projects.
2. Move the extracted projects to the GNS3 `projects` folder:
   ```bash
   mv /path/to/extracted/projects /home/your-username/GNS3/projects
   ```

#### e. Encode Project IDs to the Database
1. Use the GNS3 API to get each project’s `projectId`.
2. Add the `projectId` to your database.

---

### 8. Run the Django Server

#### a. Set Up the Virtual Environment
```bash
python3 -m venv env
source env/bin/activate
```

#### b. Install Dependencies
```bash
pip install -r requirements.txt
```

#### c. Apply Migrations and Run the Server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

## Admin Credentials
Use these credentials to log in to the admin panel:
- **Username:** `admin@gmail.com`
- **Password:** `admin@gmail.com`

---

## Troubleshooting
- **Cannot start server:** Ensure the virtual environment is activated and dependencies are installed.
- **GNS3 appliances not working:** Verify the correct host binding IP address and paths to IOS and IOU images.

Let us know if you encounter any issues during setup!
