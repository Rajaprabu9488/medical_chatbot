import AudioMessage from "./AudioMessage";
import delete_icon from './assets/delete_trash.png'
import './AudioMessage.css'
function Audiouploader({src, removeAudio}){

    return (
        <>
        <div className="audio_upload_preview">
          <AudioMessage src={src}/>
          <button className="audio_preview_delete" onClick={removeAudio}><img src={delete_icon} height='20px'></img></button>  
        </div>

        </>
    )
}
export default Audiouploader;