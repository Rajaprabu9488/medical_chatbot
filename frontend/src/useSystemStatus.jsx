import { useEffect, useState } from "react";

export const useSystemStatus = () => {
  const [network, setNetwork] = useState(navigator.onLine);
  const [mic, setMic] = useState("checking"); 

  // 🌐 Network
  useEffect(() => {
    const online = () => setNetwork(true);
    const offline = () => setNetwork(false);

    window.addEventListener("online", online);
    window.addEventListener("offline", offline);

    return () => {
      window.removeEventListener("online", online);
      window.removeEventListener("offline", offline);
    };
  }, []);

  // 🎤 Microphone
  const checkMic = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasMic = devices.some(d => d.kind === "audioinput");

      if (!hasMic) {
        setMic("not-found");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(t => t.stop());
      setMic("granted");
    } catch {
      setMic("denied");
    }
  };

  return { network, mic, checkMic };
};
