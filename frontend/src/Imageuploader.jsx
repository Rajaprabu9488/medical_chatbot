import { useState } from 'react';
import './imageuploader.css'
import cancel_icon from './assets/cancel_icon.png'

function ImageUploader({hasstarted, imageview, removeImage}){
    const [ishover, setishover]=useState(false);

    return (
        <>
        
            <div className={(hasstarted)?'image_box_started':'image_box'}>
                <div 
                onMouseEnter={()=>{setishover(true)}}
                onMouseLeave={()=>{setishover(false)}}
                className='image_on_screen'>
                <img className='pic' src={imageview} height='70px' alt='upload image'></img>
                {ishover &&
                    <button className='cancel_button' onClick={removeImage}><img className='cancel_img' src={cancel_icon} alt='upload image'></img></button>
                }
                </div>
            </div>
        </>
    )
}

export default ImageUploader;