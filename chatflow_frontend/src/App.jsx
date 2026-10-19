import React, {useState} from "react";
import Login from "./screens/Login";
import Signup from "./screens/Signup";
import Home from "./screens/Home";
import Chat from "./screens/Chat";
import Notifications from "./screens/Notifications";
import Settings from "./screens/Settings";

export default function App() {
  const [screen, setScreen] = useState("login");
  const [chat, setChat] = useState(null);

  if (screen === "login") return <Login onLogin={(userId)=>{if(Number.isInteger(userId))setScreen("home");}} onSignup={()=>setScreen("signup")} />;
  if (screen === "signup") return <Signup onBack={()=>setScreen("login")} onCreated={()=>setScreen("login")} />;
  if (screen === "chat") return <Chat chat={chat} onBack={()=>setScreen("home")} />;
  if (screen === "notifications") return <Notifications onBack={()=>setScreen("home")} />;
  if (screen === "settings") return <Settings onBack={()=>setScreen("home")} onSignOut={()=>setScreen("login")} />;

  return <Home
    onOpenChat={(c)=>{setChat(c); setScreen("chat");}}
    onNotifications={()=>setScreen("notifications")}
    onSettings={()=>setScreen("settings")}
    onSignOut={()=>setScreen("login")}
  />;
}