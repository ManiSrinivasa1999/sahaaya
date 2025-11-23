# Sahaaya Universal Health Guidance System

## Installation & Setup

### 1. Clone the Repository
```
git clone <repo-url>
cd sahaaya
```

### 2. Install Python Dependencies
It is recommended to use a virtual environment (or Anaconda). Then run:
```
pip install -r requirements.txt
```
### 3. Start the Backend Server
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Frontend
Open your browser and go to:
```
http://localhost:8000/app
```

## Features
- Multilingual (5 Indian languages)
- Voice & Text Input
- Offline/Online/Hybrid Modes
- Emergency Protocols
- PWA (installable, offline-capable)
