import { responseStatus } from "./App";
import { useContext } from "react";
import AudioMessage from "./AudioMessage";

// let query=[{from:'user',text:'what is python?'},{from:'bot',text:'python is the programming language'},
//     {from:'user',text:'how is it'},{from:'bot',text:'it is high level language'},
//     {from:'user',text:"what did u mean"},{from:'bot',text:'it is computer language'}];

function First_look(){
    const {hasstarted,query}=useContext(responseStatus);
    return (
        <>
        <div className='first_view'>
        { !hasstarted && <><h1>Reb-GPT</h1>
        <h1>how can i help you?</h1></>}
        {hasstarted && <div className="second_view">
            <h2>Reb-GPT</h2>
            <div className="chat_view">
            <ul>
                {query.map((msg)=>( <li
                    key={msg.id}
                    className={`chat_item ${msg.from === "user" ? "right" : "left"}`}>
                    {msg.content=='text' && <>{msg.text}</>}
                    {msg.content=='audio' && <AudioMessage key={msg.id} src={msg.text}/>}
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