import { useState } from "react";
import { useLocation } from "react-router-dom";
import './Login.css';
import Page_logo from './assets/otp.gif'
import Statuspopup from "./Statuspopup";
import PageNotFound from "./PageNotFound";

function Signup_verify(){
    const temp_location = useLocation();

    const [userid,Setuserid] = useState(temp_location.state?.id || '')
    const [check,Setcheck] = useState(temp_location.state?.check_box || '')
    const [usermail,Setusermail] = useState(temp_location.state?.email || '')
    const [OTP,SetOTP] = useState('');
    const [error,Seterror] = useState('');

    async function send_otp(){
        if(OTP.length != 6){
            Seterror('OTP must be in 6 digit');
            return
        }

        const form = new FormData();
        if(userid) form.append('userid',userid);
        if(userid) form.append('mail',usermail);
        if(OTP) form.append('OTP',OTP);
        

        const response = await fetch('http://127.0.0.1:3000/auth/signup_verification/',{
            method:'POST',
            body:form
        })
        
        const data = await response.json();
        if(!response.ok){
            Seterror(`${response.statusText} : ${data.detail}`);
            return;
        }

        if(check){
            localStorage.setItem('user_id', data.identity);
            localStorage.setItem('username',data.username);
            localStorage.setItem('usermail',data.usermail);
        }
        else{
            sessionStorage.setItem('user_id', data.identity);
            sessionStorage.setItem('username',data.username);
            sessionStorage.setItem('usermail',data.usermail);
        }
        sessionStorage.setItem("session_id", data.session);
        sessionStorage.setItem("sessionStarted", "true");
        
        location.href='/';
    }


    return (
        <>
        {(!userid || !usermail) && <><PageNotFound /></>}
        {(userid && usermail)  && <><Statuspopup errormsg={error} seterrormsg={Seterror} />
        <div className="forget_password_page">
            <div className="forget_password_image">
                <img height={'300px'} width={'300px'} src={Page_logo} alt="image"></img>
            </div>
            
            <div className="forget_password_content">
                <h2>SignUP VERIFICATION</h2>
                <p>Please verify your email address. We have sent a One-Time Password (OTP) to your email. Enter the OTP below to continue.</p>
                <p>your Email : <b>{usermail}</b></p>
                <div className="otp_enter">
                    <p>OTP : </p><input type="text" value={OTP} onChange={(e)=>SetOTP(e.target.value)}></input>
                </div>
                
                <p>Click "SUBMIT" button, To Continue</p>
                <div className="forget_password_button_ctrl">
                <button className="forget_password_btn" onClick={send_otp} >SUBMIT</button>
                </div>
                
            </div>
            


            </div></>}
        
        </>
    )
}

export default Signup_verify;