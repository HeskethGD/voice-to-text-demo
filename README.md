# Voice-to-text Chatbot with Streaming

This project builds a chatbot that takes text or voice inputs. It uses OpenAI Whisper for transcribing audio, and OpenAI gpt-4o-mini for providing LLM responses in the chat. It uses Django REST Framework as the backend API, Streamlit for the UI, and the `audio_recorder_streamlit` plugin for voice recording.

## Prerequisites

- Python 3.11 or higher
- Poetry (package manager)
- Git

## Project structure

The `vt_demo` folder is the root folder for the Django project, the `chatbot_app` is a Django app folder containing the core AI logic and related views, and the `ui` folder contains the Streamlit frontend.

## Getting started

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Install Poetry** (if not already installed)

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

## Configuration

1. **Set up environment variables:** Create a `.env` file, add your OpenAI API key, and Django dev secret key.

   ```
   OPENAI_API_KEY="sk-..."
   DJANGO_SECRET_KEY="django-..."
   ```

2. **Database Setup**
   ```bash
   poetry run python manage.py migrate
   ```

## Running the Application

1. **Split terminal:** You can then run the backend in one, and the frontend in another.

2. **Start the development backend server in one terminal**

   ```bash
   poetry run python manage.py runserver
   ```

   The application will be available at `http://localhost:8000`

3. **Start the UI in the other terminal**
   ```bash
   poetry run streamlit run ui/streamlit_app.py
   ```
   Navigate to `http://localhost:8501/admin` or whatever the link in the terminal suggests for the UI.

## Common Development Tasks

- **Create new migrations**

  ```bash
  poetry run python manage.py makemigrations
  ```

- **Run tests**

  ```bash
  poetry run python manage.py test
  ```

- **Install new dependencies**
  ```bash
  poetry add package-name
  ```
