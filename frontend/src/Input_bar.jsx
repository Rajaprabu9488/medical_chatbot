import {useState,useContext,useRef,useEffect} from 'react'
import mic_idle from './assets/mic_idle.png';
import send_img from './assets/send.png';
import image_upload_icon from './assets/image_upload_icon.png';
import { responseStatus } from "./App";
import Audiorecorder from './Audiorecorder';
import './Input_bar.css'
import ImageUploader from './Imageuploader';
import Audiouploader from './Audiouploader';
import { Textmessageform, Audiomessageform, Imagemessageform } from './Messageformats';
import Statuspopup from './Statuspopup';



function Input_bar(){
    const [words,Setwords]=useState('');
    const [audiosize,setaudiosize] = useState(null);
    const [imagesize,setimagesize] = useState(null); 
    const [errormsg,seterrormsg] = useState(''); 

    const {hasstarted, Sethasstarted, Setquery,recording, setRecording,audioBlob,setAudioBlob,audioview, setAudioview,
              imageview, setImageview,imageFile,setimageFile} = useContext(responseStatus);
    const fileInputRef = useRef(null);



// SESSION START
useEffect(() => {
  const sessionExists = sessionStorage.getItem("sessionStarted");
  if (sessionExists !== "true") {
    fetch("http://127.0.0.1:3000/api/session-start")
      .then(res => res.json())
      .then(data => {
        sessionStorage.setItem("session_id", data.connection);
        sessionStorage.setItem("sessionStarted", "true");
      });

    console.log("start page");
  }
}, []);

    // heartbeat method to stay alive
    useEffect(() => {
  
  
  const sendHeartbeat = () => {
    const sessionId = sessionStorage.getItem("session_id");
    if(!sessionId){
      seterrormsg('Session id is not exists, Please reload the page');
      clearInterval(interval)
      return;
    }
    fetch("http://127.0.0.1:3000/api/session-active", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ session_id: sessionId }),
    })
    .then(res => res.json())
    .then(data => console.log("heartbeat sent", data))
    .catch(err => {console.error(err)});
  };

  const interval = setInterval(sendHeartbeat, 600000);

  return () => clearInterval(interval);
}, []);

    
   

    // when user selects image file
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setimagesize((file.size / (1024 * 1024)).toFixed(2));
      setimageFile(file);
      const imageUrl = URL.createObjectURL(file);
      setImageview(imageUrl);
    }
    event.target.value = "";
  };

  const removeImage = () => {
    setImageview(null);
    setimageFile(null);
    setimagesize(null);
    fileInputRef.current.value = null;
  };

  // when user selects audio file
  const start_audiorecord = ()=>{
    setRecording(true);
    Setwords('');
  }

  const removeAudio= ()=>{
    setAudioBlob(null);
    setAudioview(null);
    setaudiosize(null);
  }

  // when user type text or click send button
  const word_change=()=>{
    const sessionExists = sessionStorage.getItem("sessionStarted");
    if (sessionExists !== "true"){
      seterrormsg('invalid session: please reload the page to get token');
      return;
    }
    Setwords(words.trim());
    if(!words && !audioBlob && !imageFile) return ;

    if(words.length >=300){
      seterrormsg('TOO MUCH OF WORDS IN PROMPT');
      return;
    }
    if(audiosize > 5) {
      seterrormsg('AUDIO SIZE IS TOO HIGH');
      return;
    }
    if(imagesize > 10) {
      seterrormsg('IMAGE FILE SIZE IS TOO HIGH');
      return;
    }
    if(imageFile){
      let image_layout;
      if(words){
        image_layout = Imagemessageform(imageview,words,false);
      }
      else if(audioBlob){
        image_layout = Imagemessageform(imageview,audioview,true);
      }
      else{
        image_layout = Imagemessageform(imageview, null,false);
      }

      Setquery(prev => [...prev,...image_layout]);
    }

    else if(words){
      const text_layout = Textmessageform(words)
      Setquery(prev=>[...prev,...text_layout]);
    }

    else if(audioBlob){
      const audio_layout = Audiomessageform(audioview);
      Setquery(prev => [...prev,...audio_layout]);
    }

    

    Api_calls();
    setaudiosize(null);
    setimagesize(null);
  }

  // send to backend server

  async function Api_calls(){
    const formData = new FormData();
    const sessionExists = sessionStorage.getItem("sessionStarted");
    if (sessionExists === "true") formData.append("session_id",sessionStorage.getItem("session_id")) 
    if(words) formData.append("text", words);
    if(audioBlob) formData.append("audio", audioBlob,`${crypto.randomUUID()}.webm`);
    if(imageFile){
      const extension = imageFile.type.split("/")[1];
      const newFileName = `${crypto.randomUUID()}.${extension}`;
      formData.append("image", imageFile,newFileName);
    } 
    Setwords('');
    setAudioBlob(null);
    setimageFile(null);
    setImageview(null);
    setAudioview(null);
    const response = await fetch("http://127.0.0.1:3000/input/", {
    method: "POST",
    body: formData
    });
    if(!response.ok){
      const error_data= await response.json();
      seterrormsg(`${response.statusText}:${error_data.detail}`);
      sessionStorage.setItem("sessionStarted", "false");
      return;
    }
    Sethasstarted(true);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let fullText = "";

    while (true) {

      const { done, value } = await reader.read();

      if (done) break;

      const chunk = decoder.decode(value);

      fullText += chunk;

      Setquery(prev => {
        const updated = [...prev];
        updated[updated.length - 1].text = fullText;
        return updated;
      });
}
  
}
 const textareaRef = useRef(null);

  // Auto resize logic
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return; 
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  }, [words]);

    return (
        <>
        <Statuspopup shownetworkstatus={true} errormsg={errormsg} seterrormsg={seterrormsg}/>
        <div className={(hasstarted)?'input_section_hasstarted':'input_section'}>
        

        {imageview && <ImageUploader hasstarted={hasstarted} imageview={imageview} removeImage={removeImage}/>}

        {!recording ? (<>
         <div className='input_container'>
          <div className='Btn-section-right'>
            <input
          type="file"
          ref={fileInputRef}
          multiple={false}
          style={{ display: "none" }}
          accept="image/*"
          onChange={handleImageChange}
        />
          <button className='input_button'
          type="button"
          onClick={() => fileInputRef.current.click()}><img src={image_upload_icon} height='30px' alt='Attach image'></img></button>
        </div>
        
         {!audioBlob ?(<textarea
        ref={textareaRef}
        maxLength={300}
        value={words}
        placeholder="Type a message"
        onChange={(e) => Setwords(e.target.value)}
        className="chat-textarea"
      />):(<Audiouploader src={audioview} removeAudio={removeAudio}/>) }
         <div className='Btn-section-left'>
          <button className='input_button' onClick={start_audiorecord}><img src={mic_idle} height='30px' alt='mic'></img></button>
      <button className='input_button' onClick={word_change}><img src={send_img} height='30px' alt='send'></img></button>
      </div>
      </div>
        
      </>
       ):(
        <Audiorecorder recording={recording} setRecording={setRecording} 
                      Setquery={Setquery} Sethasstarted={Sethasstarted} 
                      setAudioBlob={setAudioBlob} setAudioview={setAudioview} setaudiosize={setaudiosize}/>
      )}
         
      </div>
        </>
    )       
}


export default Input_bar;