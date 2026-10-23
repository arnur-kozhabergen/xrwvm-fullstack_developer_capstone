import React,{useState} from 'react';
import Header from '../Header/Header';
import {post} from '../../api';
export default function Login() {
  const [userName,setName]=useState(''),[password,setPassword]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  async function submit(e){e.preventDefault();setBusy(true);setError('');try {await post('/djangoapp/login',{userName,password});window.location.assign('/');}catch(e){setError(e.message);setBusy(false);}}
  return <><Header/><main id='main' className='auth-layout'><div><p className='eyebrow'>YOUR DEALERSHIP COMMUNITY</p><h1>Welcome back.</h1><p>Sign in to share your experience and help another driver choose with confidence.</p></div><form className='form-card' onSubmit={submit}><h2>Log in</h2><label>Username<input required autoComplete='username' value={userName} onChange={e=>setName(e.target.value)}/></label><label>Password<input required type='password' autoComplete='current-password' value={password} onChange={e=>setPassword(e.target.value)}/></label>{error&&<p role='alert' className='error'>{error}</p>}<button disabled={busy}>{busy?'Signing in…':'Log in'}</button><p>New here? <a href='/register/'>Create an account</a></p></form></main></>;
}
