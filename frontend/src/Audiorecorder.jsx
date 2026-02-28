import { useRef, useState, useEffect } from "react";
import './Audiorecorder.css';
import microphone from "./assets/mic_idle.png"
import pause from './assets/pause.png'
import resume_btn from './assets/resume.png'
import stop from './assets/stop.png'
import radio from './assets/mic_start.png'
import Statuspopup from "./Statuspopup";



const Audiorecorder= ({recording, setRecording,setAudioBlob,setAudioview, setaudiosize}) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // const [recording, setRecording] = useState(false);
  // const [audioBlob, setAudioBlob] = useState(null);
  const [paused, setPaused] = useState(false);
  const [micTrigger, setMicTrigger] = useState(false);

  let audiofile;

  // 🎤 Start Recording
  const startRecording = async () => {
    setMicTrigger(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Media recorder (actual audio)
    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (event) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorderRef.current.onstop = async () => {
    const blob = new Blob(audioChunksRef.current, {
    type: "audio/webm",
    });

    setAudioBlob(blob); 
    setAudioview(URL.createObjectURL(blob));
    setaudiosize((blob.size / (1024 * 1024)).toFixed(2));
    
    // sendAudioToDeepgram(blob);
};


    mediaRecorderRef.current.start();

    // web audio API (waveform)
    audioContextRef.current = new AudioContext();
    const source = audioContextRef.current.createMediaStreamSource(stream);

    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 2048;

    source.connect(analyserRef.current);
    dataArrayRef.current = new Uint8Array(analyserRef.current.fftSize);

    setRecording(true);
    drawWave();
  };

  // ⏹ Stop Recording
  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    cancelAnimationFrame(animationRef.current);
    audioContextRef.current.close();
    setRecording(false);
    setPaused(false);
    // setTyping(true); // set for disable mic recoding while typing in text area
    
  };

  
  // Pause Recording
  const pauseRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.pause();
      setPaused(true);
      cancelAnimationFrame(animationRef.current);
    }
  };

  // Resume Recording
  const resumeRecording = () => {
    if (mediaRecorderRef.current && recording && paused) {
      mediaRecorderRef.current.resume();
      setPaused(false);
      drawWave(); 
    }
  };


  // Draw waveform
  const drawWave = () => {
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);

      analyserRef.current.getByteTimeDomainData(dataArrayRef.current);

      ctx.fillStyle = "#020617";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 2;
      ctx.beginPath();

      const sliceWidth = canvas.width / dataArrayRef.current.length;
      let x = 0;

      for (let i = 0; i < dataArrayRef.current.length; i++) {
        const v = dataArrayRef.current[i] / 128;
        const y = (v * canvas.height) / 2;

        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        x += sliceWidth;
      }

      ctx.stroke();
    };

    draw();
  };

  // sent to tauri backend
//   const sendAudioToDeepgram = async (blob) => {
//   if (!blob) return;

//     const audiofile = URL.createObjectURL(blob);
//   const id = Date.now();

//   Setquery(prev => [
//     ...prev,
//     {
//       id: id,
//       from: 'user',
//       content: 'audio',
//       text: audiofile
//     },
//     {
//       id: id + 1,
//       from: 'bot',
//       content: 'text',
//       text: 'Typing...'
//     }
//   ]);
//   console.log(query)
// };

useEffect(() => { 
  if (recording) { startRecording(); 

  } }, [recording]);


  return (
    <>
     <Statuspopup triggerMicCheck={micTrigger} /> {/* show network and mic permission status */}
     <div className={(recording)?'audio-container':'audio_container_idle'}>
  <canvas ref={canvasRef} className={recording ? "active-canvas" : "disabled-canvas"}></canvas>

  {/* {!recording ? (<></>
    // before start recording
    // <button className="start_button" onClick={Typing ? undefined : startRecording} disabled={Typing}>
    //   <img height="30px" width="30px" src={microphone} />
    // </button>
    // <button className='button1' onClick={Typing ? undefined : startRecording} disabled={Typing}>
    //   <img src={microphone} height='30px' alt='mic'></img>
    //   </button>
  ) : ( */}
    {/* // during recording (until stop recording) */}
    
   {recording && <div className="stop_btn_mechanism">
      <button onClick={stopRecording} className="stop_button">
        <img height="50px" width="50px" src={stop}/>
      </button>

      <button className="start_button">
        <img height="50px" width="50px" src={radio} />
      </button>

      {!paused ? (
        <button onClick={pauseRecording} className="stop_button">
          <img height="50px" width="50px" src={pause}  />
        </button>
      ) : (
        <button onClick={resumeRecording} className="stop_button">
          <img height="50px" width="50px" src={resume_btn} />
        </button>
      )}
    </div>} 
  {/* )} */}
</div>
    </>
   

  );
};



export default Audiorecorder;
