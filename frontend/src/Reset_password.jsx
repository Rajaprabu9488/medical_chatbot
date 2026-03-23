import { useEffect, useState } from "react";
import { useLocation,useNavigate } from "react-router-dom";
import Statuspopup from "./Statuspopup";
import PageNotFound from "./PageNotFound";
import './Login.css';
import Page_logo from './assets/Face_scanning.gif'
import update_img from './assets/update_success.gif'
import fixed from './assets/transparent_fixed.png'

function Reset_password(){
    const temp_location = useLocation();
    const navigate = useNavigate();

    const [usermail,Setusermail] = useState(temp_location.state?.Email || '')
    const [resetKey,SetresetKey] = useState(temp_location.state?.reset_key || '')
    const [error,Seterror] = useState('');

    const [password, Setpassword] = useState('');
    const [confPassword, Setconfpassword] =useState('');
    const [ispasswordUpadated, SetispasswordUpadated] = useState(false);

    const [ended, setEnded] = useState(false);

    useEffect(() => {
        if(ispasswordUpadated){
            const timer = setTimeout(() => {
            setEnded(true);
            }, 1300); // duration of GIF (ms)

            return () => clearTimeout(timer);
        }
        
    }, [ispasswordUpadated]);

    async function Update_password(){
        if(!password || !confPassword){
            Seterror('Update the new password');
            return;
        }
        if(password.length >16 || password.length<5){
            Seterror('Password must be 5 to 16 characters');
            return;
        }
        if(password !== confPassword){
            Seterror('Password and Confirm password should be same...');
            return;
        }

        const form = new FormData()

        if(usermail) form.append('usrmail',usermail);
        if(resetKey) form.append('reset_key',resetKey);
        if(password) form.append('new_password',password);

        const response = await fetch('http://127.0.0.1:3000/auth/reset_password/',{
            method:'POST',
            body:form
        });

        const data = await response.json();

        if(!response.ok){
            Seterror(`${response.statusText} : ${data.detail}`);
            return;
        }

        SetispasswordUpadated(data['reset_status']);
    }


    return (<>
    {((!usermail || !resetKey) && !ispasswordUpadated) && <><PageNotFound /></>}
        {(usermail && resetKey) && !ispasswordUpadated && <><Statuspopup errormsg={error} seterrormsg={Seterror} />
        <div className="forget_password_page">
            <div className="forget_password_image">
                <img height={'250px'} width={'250px'} src={Page_logo} alt="image"></img>
            </div>
            
            <div className="forget_password_content">
                <h2>CONFIRM PASSWORD</h2>
                <p>Enter your New Password</p>
                <p>your Email : <b>{usermail}</b></p>
                <div className="password_enter">
                    <div className="inline_input_span"><p>Password</p><span>:</span><input type="text" value={password} onChange={(e)=>Setpassword(e.target.value)}></input></div>
                    <div className="inline_input_span"><p>Confirm password</p><span>:</span><input type="text" value={confPassword} onChange={(e)=>Setconfpassword(e.target.value)}></input></div>
                </div>
                
                <div className="reset_password_button_ctrl">
                <button className="forget_password_btn" onClick={Update_password}>SUBMIT</button>
                </div>
                
            </div>
            


            </div></>}
            {ispasswordUpadated && <div className="forget_password_page">
                <div className="update_success">
                    <img src={ended ? fixed:update_img} height={'150px'} width={'150px'} alt="gif"></img>
                    <h1>The New Password Successfully Updated...</h1>
                    
                    <button className="forget_password_btn" onClick={()=>navigate('/login')}>CONTINUE</button>
                    
                </div>
                
            </div>

            }
    </>)

}

export default Reset_password;