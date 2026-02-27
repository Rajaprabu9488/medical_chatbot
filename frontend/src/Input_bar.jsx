import {useState,useContext,useRef,useEffect} from 'react'
import mic_idle from './assets/mic_idle.png';
import send_img from './assets/send.png';
import image_upload_icon from './assets/image_upload_icon.png';
import { responseStatus } from "./App";
import Audiorecorder from './Audiorecorder';
import './Input_bar.css'
import AudioMessage from './AudioMessage';




function Input_bar(){
    const [words,Setwords]=useState('');
    const {hasstarted,Sethasstarted,Setquery,recording, setRecording,audioBlob,setAudioBlob}=useContext(responseStatus);
    const iconRef = useRef(null);

  const word_change=()=>{
    if(!words.trim() && !audioBlob) return ;
    const id = Date.now();
    if(words.trim()){
    Setquery(prev=>[...prev,{id:id,from:'user',content:'text',text:words},{id:id+1,from:'bot',content:'text',text:'Typing...'}]);
    }
    if(audioBlob){
    const audiourl=(URL.createObjectURL(audioBlob));
    
    Setquery(prev => [
      ...prev,
      {
        id: id,
        from: 'user',
        content: 'audio',
        text: audiourl
      },
      {
        id: id + 1,
        from: 'bot',
        content: 'text',
        text: 'Typing...'
      }
    ]);
    
    }
    Api_calls();
    Sethasstarted(true);
  }

  function Api_calls(){
    const formData = new FormData();

    if(words) formData.append("text", words);
    if(audioBlob) formData.append("audio", audioBlob,'recording.webm');
    // if(imageFile) formData.append("image", imageFile);
    let responses=fetch("http://127.0.0.1:3000/input/", {
    method: "POST",
    body: formData
  }).then(responded => responded.json())
  .then(data => {console.log(data);Setquery(prev => {
  const updated = [...prev];
  updated[updated.length - 1].text = data.response;
  return updated;
});
});
  Setwords('');
  setAudioBlob(null);
}
 const textareaRef = useRef(null);

  // Auto resize logic
  useEffect(() => {
    const textarea = textareaRef.current;
    const iconbox = iconRef.current;
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
    iconbox.style.top = (textarea.scrollHeight<140)?textarea.scrollHeight - iconbox.offsetHeight - 10 + "px":iconbox.style.top;
  }, [words]);
    return (
        <>
        <div className={(hasstarted)?'input_section_hasstarted':'input_section'}>
        
      
        {!recording ? (<>
         <div className='input_container'>
          <div className='Btn-section-right'>
          <button className='input_button' ><img src={image_upload_icon} height='30px' alt='Attach image'></img></button>
        </div>
        
         {!audioBlob ?(<textarea
        ref={textareaRef}
        maxLength={500}
        value={words}
        placeholder="Type a message"
        onChange={(e) => Setwords(e.target.value)}
        className="chat-textarea"
      />):(<AudioMessage src={URL.createObjectURL(audioBlob)}/>) }
         <div ref={iconRef} className='Btn-section-left'>
          <button className='input_button' onClick={()=>{setRecording(true)}}><img src={mic_idle} height='30px' alt='mic'></img></button>
      <button className='input_button' onClick={word_change}><img src={send_img} height='30px' alt='send'></img></button>
      </div>
      </div>
        
      </>
       ):(
        <Audiorecorder recording={recording} setRecording={setRecording} Setquery={Setquery} Sethasstarted={Sethasstarted} setAudioBlob={setAudioBlob}/>
      )}
         
      </div>
        </>
    )       
}


export default Input_bar;