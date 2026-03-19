import { responseStatus } from "./App";
import { useContext } from "react";
import AudioMessage from "./AudioMessage";
import Imagemessage from "./Imagemessage";

// let query=[{from:'user',text:'what is python?'},{from:'bot',text:'python is the programming language'},
//     {from:'user',text:'how is it'},{from:'bot',text:'it is high level language'},
//     {from:'user',text:"what did u mean"},{from:'bot',text:'it is computer language'}];

function First_look(){
    const {hasstarted,query}=useContext(responseStatus);
    return (
        <>
        <div className='first_view'>
        { !hasstarted && <><div style={{height:'130px'}}></div><div className="title_name"><h1 className="first_title_word">MEDY</h1><h1 className="second_title_word">- GPT</h1></div>
        <h1>how can i help you?</h1></>}
        {hasstarted && <div className="second_view">
            <div className="title_name"><h2 className="first_title_word">MEDY</h2><h2 className="second_title_word">- GPT</h2></div>
            <div className="chat_view">
            <ul>
                {query.map((msg)=>( <li
                    key={msg.id}
                    className={`chat_item ${msg.from === "user" ? "right" : "left"}`}>
                    {msg.content=='text' && <>{msg.text}</>}
                    {msg.content=='audio' && <AudioMessage key={msg.id} src={msg.text}/>}
                    {msg.content=='image' && <Imagemessage key={msg.id} src={msg.image} content={msg.text} isaudio={msg.audio}/>}
                    </li>
                ))
                }
            </ul>
            
            </div>
            </div>}
        </div>
        </>
    )
}

export default First_look;