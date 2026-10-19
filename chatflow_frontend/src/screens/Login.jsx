import React,{useState} from "react";
import {Eye,EyeOff,LockKeyhole,Mail,MessageCircle} from "lucide-react";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export default function Login({onLogin,onSignup}) {
  const [show,setShow]=useState(false);
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [error,setError]=useState("");
  const [submitting,setSubmitting]=useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const loginResponse=await fetch(`${API_BASE_URL}/auth/login`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({email:email.trim(),password}),
      });
      const loginResult=await loginResponse.json().catch(()=>({}));

      if(loginResponse.status===401) {
        setError("Wrong email or password.");
        return;
      }
      if(!loginResponse.ok) {
        throw new Error(typeof loginResult.detail==="string"?loginResult.detail:"Unable to sign in. Please try again.");
      }
      if(typeof loginResult.access_token!=="string"||!loginResult.access_token) {
        throw new Error("Unable to verify your account. Please try again.");
      }

      const userResponse=await fetch(`${API_BASE_URL}/auth/me`,{
        headers:{Authorization:`Bearer ${loginResult.access_token}`},
      });
      const user=await userResponse.json().catch(()=>({}));
      if(!userResponse.ok||!Number.isInteger(user.id)) {
        throw new Error("Unable to verify your account. Please try again.");
      }

      onLogin(user.id);
    } catch(requestError) {
      setError(requestError instanceof TypeError?"Unable to connect to the server. Please try again.":requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return <div className="auth-page"><div className="auth-card">
    <div className="brand-lockup"><div className="brand-icon"><MessageCircle size={24}/></div><div><h1>ChatFlow</h1><p>Real-time conversations, built to scale.</p></div></div>
    <div className="auth-heading"><h2>Welcome back</h2><p>Sign in to continue to your conversations.</p></div>
    <form className="form-stack" onSubmit={submitLogin}>
      <label>Email</label><div className="input-wrap"><Mail size={18}/><input type="email" placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)} required/></div>
      <label>Password</label><div className="input-wrap"><LockKeyhole size={18}/><input type={show?"text":"password"} placeholder="Enter your password" value={password} onChange={e=>setPassword(e.target.value)} required/><button type="button" className="icon-button" onClick={()=>setShow(!show)}>{show?<EyeOff size={18}/>:<Eye size={18}/>}</button></div>
      <div className="form-row between"><label className="checkbox-row"><input type="checkbox"/> Remember me</label><button type="button" className="text-button">Forgot password?</button></div>
      {error&&<p role="alert" style={{color:"#b42318",fontSize:13,margin:"4px 0"}}>{error}</p>}
      <button className="primary-button" disabled={submitting}>{submitting?"Signing in...":"Sign in"}</button>
    </form>
    <div className="divider"><span>or</span></div>
    <button className="secondary-button">Continue with Google</button>
    <p className="auth-footer">Don't have an account? <button className="text-button" onClick={onSignup}>Create one</button></p>
  </div></div>;
}