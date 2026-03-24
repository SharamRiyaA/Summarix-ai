# Summarix

Summarix is a full-stack multimodal summarization application built with Django and React. It lets a user submit text, PDF files, images, and YouTube links, then generates a saved summary in either `Short Summary` or `Key Points` mode. The app also includes authentication, per-user history, optional speech playback, OCR support for images, and a modern dashboard UI.

## What The App Does

Summarix is designed to help users quickly understand long or unstructured content.

With this app, a user can:

- paste plain text and generate a summary
- upload a PDF and summarize its extracted content
- upload an image and extract text using OCR before summarizing it
- paste a YouTube link and summarize the transcript
- choose whether they want a short summary or key points
- save every result to their personal history
- copy saved summaries easily
- generate speech output for summaries

## Project Structure

- `backend/`
  Django REST API for authentication, content extraction, summarization, OCR integration, history, and media handling.
- `frontend/`
  React + Vite application for login, summary creation, notifications, history filters, copy actions, and dashboard UI.

## Technologies Used

### Database

- `SQLite`
  This project uses SQLite as the default database. It stores:
  - registered users
  - authentication-related user records
  - saved summary history
  - extracted text
  - summary output
  - uploaded file references
  - generated audio file references

### Backend

- `Django`
  Main backend framework. Used to manage models, settings, file uploads, media, and server configuration.
- `Django REST Framework`
  Used to build REST APIs for login, registration, summary creation, listing history, viewing detail, and deleting records.
- `djangorestframework-simplejwt`
  Used for JWT-based authentication so users can log in securely and access protected routes.
- `django-cors-headers`
  Used to allow the React frontend to communicate with the Django backend from a different local port.
- `OpenAI Python SDK`
  Used to generate high-quality summaries when an `OPENAI_API_KEY` is configured.
- `requests`
  Used internally by dependencies such as transcript fetching and API-related network operations.
- `python-dotenv`
  Used to load environment variables from `.env`.
- `pypdf`
  Used to extract text from uploaded PDF files.
- `Pillow`
  Used to open and process image files before OCR.
- `pytesseract`
  Used to run OCR on uploaded images.
- `youtube-transcript-api`
  Used to fetch transcript text from YouTube videos.
- `pyttsx3`
  Used to generate local speech audio from the created summary.
- `SQLite`
  Default database used to store users and saved summary records.

### Frontend

- `React`
  Used to build the interactive UI and component-based pages.
- `React DOM`
  Used to render the React application in the browser.
- `React Router`
  Used for navigation between login, summary, and history pages.
- `Axios`
  Used for frontend-to-backend API requests.
- `localStorage`
  Used in the browser to store JWT access token, refresh token, and user info after login.
- `Vite`
  Used as the frontend dev server and build tool for fast local development.
- `@vitejs/plugin-react`
  Used so Vite can properly compile and run the React frontend.
- `CSS`
  Used for custom styling, layout, responsive behavior, toast notifications, and the dashboard design.

## Full Library List

### Backend Python packages

- `django`
- `djangorestframework`
- `djangorestframework-simplejwt`
- `django-cors-headers`
- `openai`
- `python-dotenv`
- `pypdf`
- `Pillow`
- `pytesseract`
- `youtube-transcript-api`
- `pyttsx3`

### Frontend npm packages

- `react`
- `react-dom`
- `react-router-dom`
- `axios`
- `vite`
- `@vitejs/plugin-react`

## Main Features

### Authentication

- user registration
- secure login with JWT
- protected routes on the frontend
- logout support

### Summarization

- summarize plain text
- summarize PDFs after extracting text
- summarize images after OCR
- summarize YouTube transcripts
- choose between:
  `Short Summary`
  `Key Points`
- OpenAI API summarization when a valid `OPENAI_API_KEY` is configured
- fallback local summarization if OpenAI is not available

### History

- each user has personal saved summaries
- history page shows previously generated outputs
- copy summary content directly
- delete saved items
- filter history by source type
- filter history by summary type
- search by title or summary
- sort by newest or oldest

### Extra Features

- optional speech generation for summaries
- toast notifications for actions like login and summary creation
- modern dashboard UI
- profile chip and top navigation

## How Summarization Works

### Text

User enters raw text, backend cleans it, then sends it to the OpenAI summarizer or fallback summarizer.

### PDF

Backend extracts text from the uploaded PDF using `pypdf`, cleans the content, then summarizes it.

### Image

Backend opens the uploaded image with `Pillow`, extracts text using `pytesseract`, then summarizes the extracted text.

### YouTube

Backend fetches transcript text using `youtube-transcript-api`, removes filler and repetition, then summarizes the cleaned transcript.

## Environment Variables

Create a file named `.env` inside `backend/`.

Example:

```env
DJANGO_SECRET_KEY=change-this-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### What each variable is for

- `DJANGO_SECRET_KEY`
  Secret key for Django.
- `DJANGO_DEBUG`
  Enables debug mode in local development.
- `DJANGO_ALLOWED_HOSTS`
  Hosts allowed to access the Django backend.
- `CORS_ALLOWED_ORIGINS`
  Frontend origins allowed to call backend APIs.
- `OPENAI_API_KEY`
  Enables OpenAI-based summarization.
- `OPENAI_MODEL`
  OpenAI model used for summary generation.
- `OPENAI_TEMPERATURE`
  Controls output randomness. Lower values make summaries more stable.
- `TESSERACT_CMD`
  Full path to `tesseract.exe` on Windows for OCR.

## Setup Guide

This section is written for someone who receives the project as a zip file.

## 1. Extract The Zip

Unzip the project to any folder, for example:

```bash
C:\Users\YourName\Desktop\Summarix
```

## 2. Install Requirements

### Required software

- Python 3.11+ recommended
- Node.js 18+ recommended
- npm
- Tesseract OCR if image summarization is needed

## 3. Backend Setup

Open a terminal inside the project folder and run:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Backend will start on:

```bash
http://127.0.0.1:8000/
```

## 4. Frontend Setup

Open a second terminal and run:

```bash
cd frontend
npm install
npm run dev
```

Frontend will start on:

```bash
http://localhost:5173/
```

## 5. If You Want Image OCR To Work

Install Tesseract OCR on Windows.

After installing, make sure `tesseract.exe` exists, usually here:

```bash
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Then add this in `backend/.env`:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Restart the backend after changing `.env`.

## 6. If You Want Better AI Summaries

Add your OpenAI API key in `backend/.env`:

```env
OPENAI_API_KEY=your-openai-api-key
```

Without this key, the app still works using the local fallback summarizer, but OpenAI summaries are usually better.

## Does This App Use OpenAI For Summarization?

Yes. The app uses the OpenAI API for summarization when a valid `OPENAI_API_KEY` is present in `backend/.env`.

How it works:

- if `OPENAI_API_KEY` is set correctly, the backend uses OpenAI to generate summaries
- if `OPENAI_API_KEY` is missing or the API request fails, the backend falls back to the built-in local summarizer

So the project is designed to work in both cases:

- with OpenAI for higher-quality summaries
- without OpenAI for offline/local fallback behavior

## API Overview

### Authentication

- `POST /api/auth/register/`
  Register a new user
- `POST /api/auth/login/`
  Login and receive JWT tokens

### Summaries

- `GET /api/summaries/`
  Get all saved summaries for the logged-in user
- `POST /api/summaries/create/`
  Create a new summary
- `GET /api/summaries/<id>/`
  Get full detail for one summary
- `DELETE /api/summaries/<id>/delete/`
  Delete a summary

## Typical User Flow

1. User registers or logs in.
2. User selects source type:
   text, PDF, image, or YouTube.
3. User chooses summary type:
   short summary or key points.
4. Backend extracts and cleans content.
5. Backend generates the summary.
6. Result is shown in the dashboard and saved to history.
7. User can copy, replay speech, filter history, or delete old records.

## Notes For Sharing This Project

If you send this project as a zip file to someone else, tell them:

- install Python and Node.js first
- install Tesseract OCR if they want image support
- create `backend/.env`
- add their own `OPENAI_API_KEY` if they want AI summaries
- run backend and frontend in separate terminals

## Troubleshooting

### Image upload fails

Possible cause:
- Tesseract OCR is not installed
- `TESSERACT_CMD` is missing or incorrect

### YouTube summary fails

Possible cause:
- transcript not available for the video
- network issue while fetching transcript

### OpenAI summaries do not work

Possible cause:
- missing or invalid `OPENAI_API_KEY`
- quota or request issue

### Frontend cannot connect to backend

Possible cause:
- backend server is not running
- frontend is using a different URL or port
- CORS origin is not configured correctly

## Current Highlights

- multimodal summarization
- JWT authentication
- saved user history
- history filters and search
- copy-to-clipboard support
- OCR support
- YouTube transcript support
- optional speech generation
- modern React dashboard
