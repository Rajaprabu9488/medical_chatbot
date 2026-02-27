import { useEffect, useState } from "react";
import { useSystemStatus } from "./useSystemStatus";
import "./Statuspopup.css";

const Statuspopup = ({ triggerMicCheck }) => {
  const { network, mic, checkMic } = useSystemStatus();
  const [popup, setPopup] = useState(null);

  // 🌐 Network logic
  useEffect(() => {
    if (!network) {
      setPopup({ msg: "❌ No internet connection", type: "offline", sticky: true });
    } else {
      setPopup({ msg: "✅ Internet connected", type: "online", sticky: false });
    }
  }, [network]);

  // 🎤 Mic logic
  useEffect(() => {
    if (!triggerMicCheck) return;

    checkMic();
  }, [triggerMicCheck]);

  useEffect(() => {
    if (mic === "checking") return;

    if (mic === "granted") {
      setPopup({ msg: "✅ Microphone connected", type: "online", sticky: false });
    } else if (mic === "denied") {
      setPopup({ msg: "❌ Microphone permission denied", type: "offline", sticky: false });
    } else {
      setPopup({ msg: "❌ Microphone not detected", type: "offline", sticky: false });
    }
  }, [mic]);

  // ⏱ Auto-hide logic
  useEffect(() => {
    if (!popup || popup.sticky) return;

    const t = setTimeout(() => setPopup(null), 1000);
    return () => clearTimeout(t);
  }, [popup]);

  if (!popup) return null;

  return (
    <div className={`network-popup ${popup.type}`}>
      {popup.msg}
    </div>
  );
};

export default Statuspopup;
