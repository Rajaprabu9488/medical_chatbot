import { useState, useEffect } from "react";

import PageNotFound from "./PageNotFound";
import Statuspopup from './Statuspopup';
import './EditProfile.css'

function EditProfile(){
    const [userId,SetuserId] = useState(localStorage.getItem('user_id') || sessionStorage.getItem('user_id') || '');
    const [username,Setusername] = useState('');
    const [mail, Setmail] = useState('');
    const [error,Seterror] =useState('');

    const [profileKey, SetprofileKey] = useState('')

    useEffect(()=>{

        const fetchData = async ()=>{
        const form = new FormData();

        if(userId) form.append('user_id',userId);

        const response = await fetch("http://127.0.0.1:3000/auth/Edit_profile/",{
            method : "POST",
            body : form
        });

        const data = await response.json()

        if(!response.ok){
            Seterror(`${response.statusText}:${data.detail}`);
            return;
        }
        console.log(data)
        Setusername(data['username']);
        Setmail(data['usermail']);
        SetprofileKey(data['key']);
    }
    fetchData();
    },[]);

    async function profile_update(){
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if(!profileKey){
            Seterror('Unauthorized log try again later....');
            return;
        }

        if(!username || !mail){
            Seterror("fill the form completely");
            return;
        }
        if(username.length < 3){
            Seterror("username must be more than 3 charaters");
            return;
        }
        if(!emailRegex.test(mail)){
            Seterror('Invalid E-mail id');
            return;
        }

        const form = new FormData();
        if(userId) form.append('userid',userId);
        if(username) form.append('username', username);
        if(mail) form.append('Email',mail);
        if(profileKey) form.append('key',profileKey);

        const response = await fetch("http://127.0.0.1:3000/auth/profile_update/",{
            method : "POST",
            body : form
        });

        const data = await response.json();

        if(!response.ok){
            Seterror(`${response.statusText}:${data.detail}`);
            return;
        }

        if(data['key'] !== profileKey){
            location.href = '/login';
            return;
        }

        if(data['status']){
            localStorage.removeItem('user_id');
            localStorage.removeItem('username');
            localStorage.removeItem('usermail');

            sessionStorage.removeItem('user_id');
            sessionStorage.removeItem('username');
            sessionStorage.removeItem('usermail');
            sessionStorage.removeItem("sessionStarted");
            sessionStorage.removeItem("session_id");

            location.href = '/login';
        }
    }
    return (
        <>
        <Statuspopup errormsg={error} seterrormsg={Seterror}/>
        {!userId && <PageNotFound />}
        {userId && <div className="edit_profile_bar">
            <h1>PROFILE</h1>
            <div className="profile_update">
                <label className="profile_label" title="user_name">username:</label>
                <input type="text" value={username} onChange={(e)=>Setusername(e.target.value)}></input>
                <label className="profile_label" title="E-mail">E-mail:</label>
                <input type="text" value={mail} onChange={(e)=>Setmail(e.target.value)}></input>
            </div>
            <button className="profile_submit_button" onClick={profile_update}>SAVE CHANGES</button>

        </div>}
        </>
    )
}

export default EditProfile;