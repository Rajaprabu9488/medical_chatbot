import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'
import './Login.css'
import Statuspopup from './Statuspopup';

function Login(){
    const [username,Setusername] = useState('');
    const [password,Setpassword] = useState('');
    const [check,Setcheck] = useState(true);
    const [error,Seterror] = useState('');
    const navigate = useNavigate();

    const handleClick = async (e) => {
        e.preventDefault();

        const form= new FormData()

        if (!username) {
            Seterror("Enter Username first");
            return;
        }

        if(username) form.append('username',username);

        const res = await fetch("http://127.0.0.1:3000/auth/get_usermail/", {
            method : "POST",
            body : form

        });
        const data = await res.json();

        if(!res.ok){
            Seterror(`${res.statusText}:${data.detail}`);
            return;
        }

        navigate("/forget_password", {
            state: { Email: data.usrmail, reset_key: data.reset_key}
        });
        };

    function validate_input(){
        if(!username || !password){
            Seterror('fill the form completely');
            return;
        }
        if(username.length<3){
            Seterror('invalid user');
            return;
        }
        login_api();
    }

    async function login_api(){
        const form = new FormData();
        if(username) form.append('username',username);
        if(password) form.append('password',password);

        const response = await fetch("http://127.0.0.1:3000/auth/login/",{
            method : "POST",
            body : form
        });

        const data = await response.json();
        if(!response.ok){
            Seterror(`${response.statusText}:${data.detail}`);
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

        location.href='/'
    }

    return (
        <>
        <Statuspopup errormsg={error} seterrormsg={Seterror}/>
        <div className="login_box">
            <label className="top_board" >CREATE THE ACCOUNT</label>
            <label title="USERNAME">USERNAME</label>
            <input className="userdetails" onChange={e => Setusername(e.target.value)} value={username} type="text"></input>
            <label title="PASSWORD">PASSWORD</label>
            <input className="userdetails" onChange={e => Setpassword(e.target.value)} value={password} type="password"></input>
            <Link className='forget_password_label' to='/forget_password' onClick={handleClick}>forget password</Link>
            <span className='remember_checkbox'>
                <input type='checkbox' checked={check} onChange={e => Setcheck(e.target.checked)} /><p>REMEMBER ALWAYS</p>
            </span>
            <br></br>
            <input className='login_submittion' type='button' value='LOG IN' onClick={validate_input}/>
        </div>
        </>
    )

}

export default Login;