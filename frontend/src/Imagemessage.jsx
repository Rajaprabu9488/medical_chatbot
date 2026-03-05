import AudioMessage from "./AudioMessage";
import './Imageuploader.css'


function Imagemessage(msg){
    
    const {src, content, isaudio} = msg;
    return(

        <>
        <div>
            {src &&
                <div className="image_in_chats">
                    <img src={src} height='90px' width='80px' alt="image display"></img>
                </div>
            }
            
            {content &&
                <div className="content_image_below">
                    {isaudio && <AudioMessage src={content}/> }
                    {!isaudio && <>{content}</>}
                </div>
            }
            
        </div>
        
        </>
    )

}

export default Imagemessage;