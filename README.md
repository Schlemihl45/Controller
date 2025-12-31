# CNC HMI Project

## Project Overview

This project is a Graphical User Interface for controlling a 3-Axis CNC-Mill using the LinuxCNC-Python API and PySide6.


## Features

- Touchscreen friendly GUI
- Data(base) driven project, file and tool management
- Real-time machine status monitoring
- G-Code simulation


---

## Architecture
The system is divided into three main layers:
1. **GUI (PySide6)** – User interface, signal-slot connections
2. **Controller API** – Wrapper for LinuxCNC Python API
3. **Hardware / LinuxCNC** – CNC machine and I/O
