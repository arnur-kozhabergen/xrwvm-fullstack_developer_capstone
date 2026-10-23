import React,{useState} from 'react';
import Header from '../Header/Header';
import {post} from '../../api';
export default function Register() {
  const [data,setData]=useState({userName:'',firstName:'',lastName:'',email:'',password:''}),[error,setError]=useState(''),[busy,setBusy]=useState(false);
  async function submit(e){e.preventDefault();setBusy(true);setError('');try{await post('/djangoapp/register',data);window.location.assign('/');}catch(e){setError(e.message);setBusy(false);}}
  return <><Header/><main id='main' className='auth-layout'><div><p className='eyebrow'>A BETTER WAY TO CHOOSE</p><h1>Your experience matters.</h1><p>Join the conversation. Save other drivers a detour by sharing an honest dealership review.</p></div><form className='form-card' onSubmit={submit}><h2>Create your account</h2>{[['userName','Username','text','username'],['firstName','First Name','text','given-name'],['lastName','Last Name','text','family-name'],['email','Email','email','email'],['password','Password','password','new-password']].map(([key,label,type,auto])=><label key={key}>{label}<input required maxLength={key==='userName'?150:254} minLength={key==='password'?8:1} type={type} autoComplete={auto} value={data[key]} onChange={e=>setData({...data,[key]:e.target.value})}/></label>)}<p className='muted'>Use at least eight characters and a password you do not use elsewhere.</p>{error&&<p role='alert' className='error'>{error}</p>}<button disabled={busy}>{busy?'Creating account…':'Register'}</button></form></main></>;
}
