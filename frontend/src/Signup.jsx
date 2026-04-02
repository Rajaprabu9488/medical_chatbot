import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css'
import Statuspopup from './Statuspopup';


function Signup(){
    const [username,Setusername] = useState('');
    const [email, Setemail] = useState('');
    const [password,Setpassword] = useState('');
    const [confpassword, Setconfpassword] = useState('');
    const [check,Setcheck] = useState(true);
    const [error,Seterror] = useState('');

    const navigate = useNavigate();

    function validate_input(){
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        if(!username || !email || !password || !confpassword){
            Seterror("fill the form completely");
            return;
        }
        if(username.length < 3){
            Seterror("username must be more than 3 charaters");
            return;
        }
        if(!emailRegex.test(email)){
            Seterror('Invalid E-mail id');
            return;
        }
        if(password.length >16 || password.length<5){
            Seterror('Password must be 5 to 16 characters');
            return;
        }
        if(password !== confpassword){
            Seterror('Password and Confirm password should be same...');
            return;
        }

        signup_api();
    }

    async function signup_api(){
        const form = new FormData();
        if(username) form.append('username',username);
        if(email) form.append('email',email);
        if(password) form.append('password',password);

        const response = await fetch("http://127.0.0.1:3000/auth/signup/",{
            method : "POST",
            body : form
        });

        const data = await response.json();
        if(!response.ok){
            Seterror(`${response.statusText} : ${data.detail}`);
            return;
        }

        
        
        navigate('/signup_verify',{
            state: { id: data.identity ,email: data.usermail, check_box:check}, replace: true 
        });
    }
        return (
            <>
            <Statuspopup errormsg={error} seterrormsg={Seterror}/>
            <div className="login_box">
                <label className="top_board">CREATE THE ACCOUNT</label>
            <label htmlFor="username" title="USERNAME">USERNAME</label>
            <input id="username" className="userdetails" onChange={e => Setusername(e.target.value)} value={username} type="text"></input>
            <label htmlFor="email" title="E-MAIL">E-MAIL</label>
            <input id="email" className="userdetails" onChange={e => Setemail(e.target.value)} value={email} placeholder='enter valid email id' type="text"></input>
            <label htmlFor="password" title="PASSWORD">PASSWORD</label>
            <input id="password" className="userdetails" onChange={e => Setpassword(e.target.value)} value={password} type="password"></input>
            <label htmlFor="confpassword" title="CONFIRM PASSWORD">CONFIRM PASSWORD</label>
            <input id="confpassword" className="userdetails" onChange={e => Setconfpassword(e.target.value)} value={confpassword} type="password"></input>
            <span className='remember_checkbox'>
                <input type='checkbox' checked={check} onChange={e => Setcheck(e.target.checked)} /><p>REMEMBER ALWAYS</p>
            </span>
            <br></br>
            <input className='login_submittion' type='button' value='SIGN IN' onClick={validate_input}/>
        </div>
        </>
        )
}
export default Signup;