## Setup Environment - Shell/Terminal
- pip install virtualenv
- mkdir Proyek
- cd Proyek
- python -m venv .env  # Membuat environment bernama .env
- .\.env\Scripts\activate  # pada powershell windows
- pip install -r requirements.txt

## Instalasi package python pada .env
- (.env) $ pip list
- (.env) $ pip freeze > requirements.txt

## Untuk menonaktifkan virtual environment:
(.env) $ deactivate

## Run streamlit app
streamlit run dashboard.py
