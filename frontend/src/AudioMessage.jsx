import { useRef, useState, useEffect } from "react";
import './AudioMessage.css'

function AudioMessage({ src }) {
  const audioRef = useRef(null);

  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  // Format time (mm:ss)
  const formatTime = (time) => {
    if (!time || isNaN(time)) return "0:00";
    const min = Math.floor(time / 60);
    const sec = Math.floor(time % 60);
    return `${min}:${sec.toString().padStart(2, "0")}`;
  };

  // Play / Pause
  const togglePlay = () => {
    const audio = audioRef.current;

    if (audio.paused) {
      audio.play();
      setPlaying(true);
    } else {
      audio.pause();
      setPlaying(false);
    }
  };

  useEffect(() => {
    const audio = audioRef.current;

    const updateProgress = () => {
      setProgress(audio.currentTime);
    };

    const setMeta = () => {
      setDuration(audio.duration || 0);
    };

    const handleEnded = () => {
      setProgress(audio.duration || 0);
      setPlaying(false);
    };

    audio.addEventListener("timeupdate", updateProgress);
    audio.addEventListener("loadedmetadata", setMeta);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", updateProgress);
      audio.removeEventListener("loadedmetadata", setMeta);
      audio.removeEventListener("ended", handleEnded);
    };
  }, [src]);

  const handleSeek = (e) => {
    const value = Number(e.target.value);
    audioRef.current.currentTime = value;
    setProgress(value);
  };

  return (
    <div className="audio-container">

      <button onClick={togglePlay} className="play-btn">
        {playing ? "⏸" : "▶"}
      </button>

      <input
        type="range"
        min="0"
        max={duration || 0}
        step="0.01"
        value={Math.min(progress, duration)}
        onChange={handleSeek}
        className="progress-bar"
      />

      {/* ✅ Time display */}
      <span className="audio-time">
        {formatTime(progress)} / {formatTime(duration)}
      </span>

      <audio ref={audioRef} src={src} preload="metadata" />

    </div>
  );
}

export default AudioMessage;