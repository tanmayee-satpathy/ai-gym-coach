<div align="center">

# AI Gym Coach

### A real-time AI fitness coach that watches your form, counts your reps, and speaks actionable coaching cues while you train.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-111827?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img alt="MediaPipe" src="https://img.shields.io/badge/MediaPipe-Pose-00A67E?style=for-the-badge">
  <img alt="OpenCV" src="https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white">
  <img alt="Groq" src="https://img.shields.io/badge/Groq-Voice_Coach-F55036?style=for-the-badge">
</p>

<p>
  <a href="#overview">Overview</a> .
  <a href="#features">Features</a> .
  <a href="#quick-start">Quick Start</a> .
  <a href="#architecture">Architecture</a> .
  <a href="#deployment">Deployment</a>
</p>

</div>

---

## Overview

AI Gym Coach is a polished Streamlit fitness dashboard that turns a webcam into a live training assistant. It uses MediaPipe pose landmarks and custom exercise detectors to track movement quality, count reps, measure set progress, save workout history, and deliver short AI-generated voice cues through a Groq-powered coaching pipeline.

The app is designed for focused solo training: choose an exercise, set your targets, start the camera, and receive real-time form feedback as you move.

## Features

| Capability | What it does |
| --- | --- |
| Live pose detection | Tracks body landmarks through the webcam using MediaPipe Pose Landmarker. |
| Automatic rep counting | Counts completed reps with exercise-specific stage logic. |
| Form quality metrics | Surfaces key movement signals such as knee angle, elbow angle, depth, alignment, swing, balance, and back arch. |
| AI voice coaching | Generates concise coaching cues with Groq and turns them into audio using gTTS. |
| Workout planning | Lets users choose exercise, sets, and reps from a clean sidebar workflow. |
| Account system | Includes sign up, login, password hashing, and per-user workout history. |
| Progress history | Saves completed work locally in SQLite and summarizes training by exercise and date. |
| Premium dashboard UI | Uses custom styling, local typography, responsive layout, and live camera overlays. |

## Supported Exercises

- Squats
- Push-ups
- Biceps Curls (Dumbbell)
- Shoulder Press
- Lunges

Each movement has its own detector, metrics, and coaching rules so feedback stays specific instead of generic.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Interface | Streamlit, custom CSS, local font assets |
| Camera stream | streamlit-webrtc, WebRTC |
| Computer vision | MediaPipe, OpenCV, NumPy, PyAV |
| Coaching intelligence | Groq chat completions |
| Voice output | gTTS |
| Data | SQLite, pandas |
| Runtime | Python 3.11 |

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-gym-coach.git
cd ai-gym-coach
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq key

Set `GROQ_API_KEY` in your shell before launching the app:

```bash
# Windows PowerShell
$env:GROQ_API_KEY="your_groq_api_key_here"

# macOS / Linux
export GROQ_API_KEY="your_groq_api_key_here"
```

For deployed Streamlit apps, add the same key to Streamlit secrets.

### 5. Run the app

```bash
streamlit run main.py
```

Open the local URL shown in your terminal, allow camera access, and start training.

## How It Works

1. The user signs in or creates an account.
2. The user selects an exercise, number of sets, and reps per set.
3. WebRTC streams webcam frames into the video processor.
4. MediaPipe detects pose landmarks from each frame.
5. The selected detector calculates movement-specific metrics and rep progress.
6. The dashboard syncs live stats into Streamlit session state.
7. When sets complete or form issues appear, the voice pipeline asks the LLM coach for a short cue.
8. The cue is converted to speech and played back in the app.
9. Completed workout progress is saved to SQLite and displayed in workout history.

## Architecture

```text
ai-gym-coach/
|-- main.py                         # Streamlit app entry point
|-- core/
|   `-- base_exercise.py            # Shared angle and landmark utilities
|-- detectors/                      # Exercise-specific rep and form detectors
|   |-- squat.py
|   |-- pushup.py
|   |-- biceps_curl.py
|   |-- shoulder_press.py
|   `-- lunges.py
|-- services/
|   |-- auth/                       # Login, sign up, password hashing
|   |-- coaching/                   # LLM coach, TTS, voice orchestration
|   |-- config/                     # Exercise options, metric fields, prompt
|   |-- persistence/                # SQLite repository
|   |-- state/                      # Streamlit session defaults
|   |-- tracking/                   # Metric syncing and workout saving
|   |-- ui/                         # CSS/font injection helpers
|   `-- vision/                     # WebRTC video processor
|-- ml_models/
|   `-- pose_landmarker_full.task   # MediaPipe pose model asset
|-- static/
|   |-- style.css                   # Premium dashboard styling
|   `-- AdobeClean.otf              # Local font
|-- requirements.txt
|-- packages.txt
`-- runtime.txt
```

## Environment Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes for AI coaching | Enables Groq-powered coaching text generation. |

Without a valid Groq key, the core vision workflow can still be explored, but AI voice coaching will not initialize.

## Deployment

This repository includes deployment-friendly files:

- `runtime.txt` pins Python 3.11.
- `packages.txt` lists Linux system packages needed by OpenCV and MediaPipe.
- `requirements.txt` pins the Python app dependencies.

For Streamlit Community Cloud or similar platforms:

1. Push the repository to GitHub.
2. Set `GROQ_API_KEY` in app secrets.
3. Use `main.py` as the app entry point.
4. Make sure the `ml_models/pose_landmarker_full.task` file is included in the repository.

## Privacy Notes

- Camera frames are processed live for pose detection inside the running app session.
- User accounts and workout history are stored in the local SQLite database.
- Coaching prompts are sent to Groq only when the voice coaching pipeline needs feedback text.

## Roadmap

- Add visual progress charts for weekly and monthly trends.
- Add workout export to CSV.
- Add configurable coaching intensity.
- Add support for more exercises.
- Add test coverage for detector thresholds and persistence flows.

## Contributing

Contributions are welcome. A good first contribution is adding a new detector, improving a form metric, or enhancing workout history visualization.

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then open a pull request with a short explanation of the change and how you tested it.

## License

No license file is currently included. Add a license before publishing if you want others to use, modify, or distribute this project.

---

<div align="center">

Built for smarter reps, cleaner form, and training sessions that feel coached from the first set.

</div>
