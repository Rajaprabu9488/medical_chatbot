import { useEffect, useState } from "react";
import { useLocation,useNavigate } from "react-router-dom";
import Statuspopup from "./Statuspopup";
import PageNotFound from "./PageNotFound";


function Forget_password(){
    const location = useLocation();
    const navigate = useNavigate();

    const [usermail,Setusermail] = useState(location.state?.Email || '')
    const [resetKey,SetresetKey] = useState(location.state?.reset_key || '')
    const [OTP,SetOTP] = useState('');
    const [error,Seterror] = useState('');


    async function send_otp(){
        if(OTP.length != 6){
            Seterror('OTP must be in 6 digit');
            return
        }

        const form = new FormData();

        if(usermail) form.append('mail',usermail);
        if(resetKey) form.append('reset_key',resetKey);
        if(OTP) form.append('OTP',OTP);
        

        const response = await fetch('http://127.0.0.1:3000/auth/OTP_verification/',{
            method:'POST',
            body:form
        })
        
        const result = await response.json();
        if(!result.ok){
            Seterror(`${response.statusText} : ${result.detail}`);
            return;
        }
    }

    


    return (
        <>
        {(!usermail || !resetKey) && <><PageNotFound /></>}
        {(usermail && resetKey)  && <><Statuspopup errormsg={error} seterrormsg={Seterror} />
        <div className="forget_password_page">
            <div className="forget_password_image">
                <img height={'250px'} width={'250px'} src="./src/assets/Face_scanning.gif" alt="image"></img>
            </div>
            
            <div className="forget_password_content">
                <h2>OTP VERIFICATION</h2>
                <p>Please verify your email address. We have sent a One-Time Password (OTP) to your email. Enter the OTP below to continue.</p>
                <p>your Email : <b>{usermail}</b></p>
                <div className="otp_enter">
                    <p>OTP : </p><input type="text" value={OTP} onChange={(e)=>SetOTP(e.target.value)}></input>
                </div>
                
                <p>Click "SUBMIT" button, To Continue</p>
                <div className="forget_password_button_ctrl">
                <button className="forget_password_btn" onClick={()=>{navigate('/login')}}>{'< Back'}</button>
                <button className="forget_password_btn" >SUBMIT</button>
                </div>
                
            </div>
            


            </div></>}
        </>
    )
}

export default Forget_password;