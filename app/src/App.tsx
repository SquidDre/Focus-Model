import React, { useState, useEffect, useRef } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';

// Professional Palette: Blue for focus, Amber/Red for distraction
const App = () => {
  const webcamRef = useRef(null);
  const [status, setStatus] = useState("Initializing...");
  const [isFocused, setIsFocused] = useState(true);
  const [seconds, setSeconds] = useState(25 * 60); // 25 Minute Pomodoro
  const [isActive, setIsActive] = useState(false);

  // 1. The AI "Heartbeat" - Snaps a photo and asks the Python Brain
  const checkFocus = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        try {
          const response = await axios.post('http://127.0.0.1:8000/predict-focus', {
            image_b64: imageSrc
          });
          const result = response.data.status;
          setStatus(result);
          setIsFocused(result === "Focused");
          
          // Auto-pause timer if user is distracted
          if (result === "Distracted") {
            setIsActive(false);
          }
        } catch (err) {
          console.error("API Offline. Make sure Uvicorn is running!");
          setStatus("Offline");
        }
      }
    }
  };

  // 2. Timer Logic
  useEffect(() => {
    let interval = null;
    if (isActive && seconds > 0) {
      interval = setInterval(() => setSeconds(s => s - 1), 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isActive, seconds]);

  // 3. AI Prediction Loop (Runs every 2 seconds to save CPU)
  useEffect(() => {
    const aiLoop = setInterval(checkFocus, 2000);
    return () => clearInterval(aiLoop);
  }, []);

  const formatTime = (s) => {
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className={`min-h-screen transition-colors duration-700 flex flex-col items-center justify-center p-6 ${
      isFocused ? 'bg-slate-50' : 'bg-red-100'
    }`}>
      
      {/* Header Section */}
      <div className="text-center mb-8">
        <h1 className={`text-5xl font-black mb-2 tracking-tight ${isFocused ? 'text-slate-900' : 'text-red-600'}`}>
          {isFocused ? "DEEP WORK" : "EYES ON SCREEN!"}
        </h1>
        <p className="text-slate-500 font-medium">AI-Powered Pomodoro Tracker</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
        
        {/* Left Side: The AI Vision */}
        <div className="bg-white p-4 rounded-3xl shadow-xl border-4 border-white">
          <div className="relative rounded-2xl overflow-hidden shadow-inner bg-slate-200 aspect-video">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              className="w-full h-full object-cover"
            />
            {/* Overlay Status Badge */}
            <div className={`absolute top-4 left-4 px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest shadow-lg ${
              isFocused ? 'bg-green-500 text-white' : 'bg-red-500 text-white animate-pulse'
            }`}>
              AI: {status}
            </div>
          </div>
        </div>

        {/* Right Side: The Timer Control */}
        <div className="bg-white p-8 rounded-3xl shadow-xl flex flex-col items-center justify-center border-4 border-white">
          <div className="text-7xl font-mono font-bold text-slate-800 mb-6">
            {formatTime(seconds)}
          </div>
          
          <div className="flex gap-4">
            <button 
              onClick={() => setIsActive(!isActive)}
              disabled={!isFocused}
              className={`px-8 py-3 rounded-2xl font-bold text-white transition-all ${
                !isFocused ? 'bg-slate-300 cursor-not-allowed' : 
                isActive ? 'bg-slate-800 hover:bg-slate-700' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-200'
              }`}
            >
              {isActive ? "PAUSE" : "START SESSION"}
            </button>
            <button 
              onClick={() => {setSeconds(25*60); setIsActive(false);}}
              className="px-6 py-3 rounded-2xl font-bold text-slate-400 hover:bg-slate-100 transition-colors"
            >
              RESET
            </button>
          </div>

          {!isFocused && (
            <p className="mt-4 text-sm text-red-500 font-semibold animate-bounce">
              Timer paused. Model detects distraction!
            </p>
          )}
        </div>
      </div>

      {/* Footer Instructions */}
      <footer className="mt-12 text-slate-400 text-sm">
        Running on <span className="font-mono bg-slate-200 px-2 py-1 rounded text-slate-600">FastAPI + PyTorch</span>
      </footer>
    </div>
  );
};

export default App;