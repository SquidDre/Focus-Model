# Temporary Read Me
# 🧠 Deep Work: AI-Powered Focus Tracker

A full-stack "Smart Pomodoro" application that uses a custom **Convolutional Neural Network (CNN)** to monitor user engagement in real-time. If the AI detects the user is distracted or looking away from the screen, it automatically pauses the focus timer and provides immediate visual feedback.

## ✨ Features
* **Real-Time Inference:** Processes webcam frames through a PyTorch model every 500ms without freezing the browser.
* **State-Driven UI:** The React frontend dynamically shifts themes (Blue for Focus, Red for Distraction) based on the AI's predictions.
* **Auto-Pausing Timer:** Integrates standard Pomodoro logic that physically stops counting down when the user loses focus.
* **Optimized CPU Execution:** The FastAPI backend decodes Base64 image strings entirely in memory (RAM) to ensure lightning-fast prediction speeds on standard hardware.

## 🚀 The Tech Stack

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React (Vite) + TypeScript | Real-time UI, state management, and Webcam interface |
| **Styling** | Tailwind CSS v4 | Utility-first styling for rapid state-driven UI changes |
| **API Server** | FastAPI (Python) | High-performance, asynchronous REST API |
| **AI Brain** | PyTorch | Custom CNN architecture for binary classification |

## 🛠️ System Architecture

1. **Vision:** The React `<Webcam />` component captures a frame and converts it to a Base64 string.
2. **Transport:** Axios sends a POST request with the Base64 payload to the FastAPI `/predict-focus` endpoint.
3. **Processing:** Python strips the metadata, decodes the binary bytes, and wraps them in a virtual file (`io.BytesIO`) to avoid slow disk reads.
4. **Inference:** The image is transformed into a 64x64 tensor and passed through the `FocusStateCNN`.
5. **Reaction:** The server returns JSON (`{"status": "Distracted"}`), and React immediately updates the UI and timer state.

## 🏁 Quick Start

### 1. Start the AI Server
```bash
# Activate your Python virtual environment
source project_env/bin/activate

# Install requirements
pip install fastapi[standard] torch torchvision pillow

# Run the Uvicorn server
uvicorn main:app --reload

# Navigate to the frontend directory
cd app

# Install dependencies
npm install
npm install @tailwindcss/postcss

# Start the Vite development server
npm run dev
