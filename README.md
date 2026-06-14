# Cyber Incident Manager

Cyber Incident Manager is a desktop application developed as a university Cyber Defense project. The system was built using Python, SQLite and CustomTkinter, following the MVC architecture pattern to provide a simple and organized platform for cybersecurity incident management.

## Features

### Authentication & Access Control

* User authentication
* Role-based permissions
* Administrator, Analyst and Viewer profiles

### Incident Management

* Create incidents
* Edit incidents
* Delete incidents
* Incident details view
* Incident ownership assignment

### Incident Tracking

* Comments
* Change history
* Timeline of events
* Audit logging

### Dashboards

* Operational dashboard
* Executive dashboard
* Incident statistics
* Severity distribution
* Status distribution

### Knowledge Base

* Internal cybersecurity articles
* Procedures and response guides
* Knowledge sharing

### Search

* Global search
* Incident lookup
* User lookup

### Data Export

* CSV export functionality

---

## Technologies

* Python 3
* SQLite
* CustomTkinter
* Tkinter
* Pandas
* Matplotlib
* PyInstaller

---

## Architecture

The project follows the MVC (Model-View-Controller) architecture:

```text
controllers/
models/
views/
database/
utils/
```

### Models

Responsible for domain entities such as users and incidents.

### Views

Graphical interface developed with CustomTkinter.

### Controllers

Business logic, permissions, validation and database operations.

### Database

SQLite local database for data persistence.

---

## User Roles

### Administrator

* Full system access
* Manage users
* Manage incidents
* Configure system settings

### Analyst

* Create incidents
* Edit incidents
* Add comments
* Access dashboards

### Viewer

* Read-only access
* View incidents
* View dashboards

---

## Project Structure

```text
CyberIncidentManager
│
├── controllers/
├── models/
├── views/
├── database/
├── utils/
│
├── main.py
├── requirements.txt
├── CyberIncidentManager.spec
└── build_exe.bat
```

---

## Installation

### Clone repository

```bash
git clone https://github.com/hiskjuc/CyberIncidentManager.git
cd CyberIncidentManager
```

### Create virtual environment

```bash
python -m venv .venv
```

### Activate environment

Windows:

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run application

```bash
python main.py
```

---

## Build Executable

```bash
pip install -r requirements-build.txt
build_exe.bat
```

Or:

```bash
pyinstaller --clean CyberIncidentManager.spec
```

---

## Academic Context

This project was originally developed for a Cyber Defense course and later expanded as a personal project for learning:

* Software architecture
* Desktop development
* Database management
* Cybersecurity workflows
* Incident response processes

---

## Artificial Intelligence Usage

The project was developed with assistance from:

* ChatGPT
* OpenAI Codex

The tools were used to assist with planning, implementation, debugging, documentation and code review. All generated code was reviewed, tested and validated before integration into the project.

---

## License

This project is available for educational and portfolio purposes.
