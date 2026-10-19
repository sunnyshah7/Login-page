import React, { useState } from "react";
import { ArrowLeft, Eye, EyeOff, LockKeyhole, Mail, UserRound, Upload } from "lucide-react";

const API_BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export default function Signup({ onBack, onCreated }) {
  const [show, setShow] = useState(false);
  const [show2, setShow2] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "", terms: false });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const updateForm = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  async function submitSignup(event) {
    event.preventDefault();
    setError("");

    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    if (!form.terms) {
      setError("Please accept the terms and privacy policy.");
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password,
        }),
      });
      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(typeof result.detail === "string" ? result.detail : "Unable to create your account.");
      }

      onCreated();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to create your account.");
    } finally {
      setSubmitting(false);
    }
  }

  return <div className="auth-page"><div className="auth-card signup-card">
    <button type="button" className="back-button" onClick={onBack}><ArrowLeft size={18}/> Back to login</button>
    <div className="auth-heading"><h2>Create your account</h2><p>Set up your ChatFlow profile in a few seconds.</p></div>
    <div className="avatar-upload"><div className="upload-avatar">R</div><button type="button" className="upload-button"><Upload size={16}/> Upload photo</button></div>
    <form className="form-stack" onSubmit={submitSignup}>
      <label htmlFor="signup-name">Full name</label><div className="input-wrap"><UserRound size={18}/><input id="signup-name" value={form.name} onChange={(event) => updateForm("name", event.target.value)} placeholder="Your name" required/></div>
      <label htmlFor="signup-email">Email</label><div className="input-wrap"><Mail size={18}/><input id="signup-email" type="email" value={form.email} onChange={(event) => updateForm("email", event.target.value)} placeholder="you@example.com" required/></div>
      <label htmlFor="signup-password">Password</label><div className="input-wrap"><LockKeyhole size={18}/><input id="signup-password" minLength={8} type={show ? "text" : "password"} value={form.password} onChange={(event) => updateForm("password", event.target.value)} placeholder="At least 8 characters" required/><button type="button" className="icon-button" aria-label={show ? "Hide password" : "Show password"} onClick={() => setShow(!show)}>{show ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div>
      <label htmlFor="signup-confirm">Confirm password</label><div className="input-wrap"><LockKeyhole size={18}/><input id="signup-confirm" type={show2 ? "text" : "password"} value={form.confirm} onChange={(event) => updateForm("confirm", event.target.value)} placeholder="Repeat your password" required/><button type="button" className="icon-button" aria-label={show2 ? "Hide password" : "Show password"} onClick={() => setShow2(!show2)}>{show2 ? <EyeOff size={18}/> : <Eye size={18}/>}</button></div>
      <label className="checkbox-row terms"><input type="checkbox" checked={form.terms} onChange={(event) => updateForm("terms", event.target.checked)}/><span>I agree to the Terms of Service and Privacy Policy.</span></label>
      {error && <p role="alert" style={{ color: "#b42318", fontSize: 13, margin: "4px 0" }}>{error}</p>}
      <button className="primary-button" disabled={submitting}>{submitting ? "Creating account..." : "Create account"}</button>
    </form>
  </div></div>;
}