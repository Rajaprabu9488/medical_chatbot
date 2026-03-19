import { useState,useEffect } from "react";
import { Link } from "react-router-dom";
import './Login.css'

function Login_signup_bar(){
    const [user_id, Setuser_id] = useState('');
    const [usrname, Setusrname] = useState('');
    const [usrmail, Setusrmail] = useState('');
    const [showpop, Setshowpop] = useState(false);

    const color = 
    useEffect(()=>{
        const from_local=localStorage.getItem('user_id');
        const from_session = sessionStorage.getItem('user_id');
        if(from_local){
            Setuser_id(from_local);
            Setusrname(localStorage.getItem('username'));
            Setusrmail(localStorage.getItem('usermail'));
        }
        if(from_session){
            Setuser_id(from_session);
            Setusrname(sessionStorage.getItem('username'));
            Setusrmail(sessionStorage.getItem('usermail'));
        }
    },[]);

    function getColorFromEmail(email) {
        let hash = 0;

        for (let i = 0; i < email.length; i++) {
            hash = email.charCodeAt(i) + ((hash << 5) - hash);
        }

        const hue = Math.abs(hash % 360);

        return `hsl(${hue}, 60%, 50%)`;
    }
    
    function profilepopup(){
        if(showpop) Setshowpop(false);
        if(!showpop) Setshowpop(true);
    }

    function sign_out(){
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('usermail');

        sessionStorage.removeItem('user_id');
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('usermail');
        sessionStorage.removeItem("sessionStarted");
        sessionStorage.removeItem("session_id")

        location.reload(true);

    }
    return (
        <>
        {!user_id && <div className="login_container">
            <Link className='login_list' to="/login">Login</Link>
            <Link className='login_list' to="/signup">Signup</Link>
        </div>
        }
        {user_id && <><div className="profile" style={{ backgroundColor: getColorFromEmail(user_id)}} onMouseEnter={profilepopup}>
            <label title={usrname}>{usrname.charAt(0)}</label><br></br>
        </div>
        {showpop && <div className="profile_list" onMouseLeave={profilepopup}>
                <ul className="profile_ul">
                <li><div><b>{usrname}</b><br></br>
                {usrmail}
                </div></li>
                <hr></hr>
                <li><button className="profile_button" onClick={()=>alert('edit profile')}>EDIT PROFILE</button></li>
                <hr></hr>
                <li><button className="profile_button" onClick={sign_out}>SIGN OUT</button></li>
            </ul>

            </div>}</>
        }
        </>
    )
}

export default Login_signup_bar;