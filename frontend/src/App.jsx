import { useState ,createContext} from 'react'
import './App.css'
import First_look from './First_look'
import Input_bar from './Input_bar'

export const responseStatus = createContext();
function App() {
  const [hasstarted,Sethasstarted]= useState(false);
  const [query,Setquery]=useState([]);
  const [recording, setRecording] = useState(false);
   const [audioBlob, setAudioBlob] = useState(null);
  return (
    <>
    <responseStatus.Provider value={{hasstarted,Sethasstarted,query,Setquery,recording, setRecording,audioBlob,setAudioBlob}}>
      <First_look />
      <Input_bar />
    </responseStatus.Provider>
    
    
        
    </>
  )
}

export default App
