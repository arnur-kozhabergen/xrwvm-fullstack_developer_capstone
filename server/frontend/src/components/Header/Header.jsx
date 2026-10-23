import React, {useState,useEffect} from 'react';
import {api} from '../../api';
export default function Header() {
  const [user,setUser]=useState('');
  const [error,setError]=useState('');
  useEffect(()=>{api('/djangoapp/session').then(x=>setUser(x.userName)).catch(()=>setError('Session unavailable'));},[]);
  async function logout(e) {e.preventDefault();try {await api('/djangoapp/logout'); sessionStorage.clear(); window.location.assign('/');} catch(e){setError(e.message);}}
  return <><a className='skip' href='#main'>Skip to content</a><header className='site-header'><a className='brand' href='/'><span className='brand-mark' aria-hidden='true'>C</span>Cars Dealership<span className='brand-sub'>FIND YOUR NEXT CONNECTION</span></a><nav aria-label='Main navigation'><a href='/'>Dealerships</a><a href='/about/'>About us</a><a href='/contact/'>Contact us</a></nav><div className='account'>{user?<><span className='user-name'>{user}</span><a href='/djangoapp/logout' onClick={logout}>Log out</a></>:<><a href='/login/'>Log in</a><a className='button compact' href='/register/'>Sign up</a></>}</div></header>{error&&<p role='alert'>{error}</p>}</>;
}
