import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState ,createContext} from 'react'
import './App.css'
import First_look from './First_look'
import Input_bar from './Input_bar'
import Login from './Login'
import Signup from './Signup'
import Login_signup_bar from "./Login_signup_bar";
import Forget_password from "./forget_password";


export const responseStatus = createContext();
function App() {
  const [hasstarted,Sethasstarted]= useState(false);
  const [query,Setquery]=useState([]);
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioview, setAudioview] = useState(null);
  const [imageview, setImageview] = useState(null);
  const [imageFile, setimageFile] = useState(null);
  return (
    <>
    <BrowserRouter>
      
        
    <responseStatus.Provider value={{hasstarted,Sethasstarted,
                        query,Setquery,
                        recording, setRecording,
                        audioBlob,setAudioBlob,audioview,setAudioview,
                        imageview,setImageview,imageFile,setimageFile}}>
      

      <Routes>
        <Route path="/" element={
      <>
        <Login_signup_bar />
        <First_look />
        <Input_bar />
      </>
  } />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forget_password" element={<Forget_password />} />
      </Routes>
    </responseStatus.Provider>
    </BrowserRouter>
    
        
    </>
  )
}

export default App
