import {render,screen} from '@testing-library/react';
import {MemoryRouter} from 'react-router-dom';
import App from './App';
beforeEach(()=>{global.fetch=jest.fn().mockResolvedValue({ok:true,json:async()=>({userName:'',dealers:[]})});});
test('registration exposes all five required labelled fields',()=>{
 render(<MemoryRouter initialEntries={['/register']}><App/></MemoryRouter>);
 for(const label of ['Username','First Name','Last Name','Email','Password']) expect(screen.getByLabelText(label)).toBeTruthy();
 expect(screen.getByRole('button',{name:'Register'})).toBeTruthy();
});
test('login has accessible username/password and action',()=>{
 render(<MemoryRouter initialEntries={['/login']}><App/></MemoryRouter>);
 expect(screen.getByLabelText('Username')).toBeTruthy();
 expect(screen.getByLabelText('Password').type).toBe('password');
 expect(screen.getByRole('button',{name:'Log in'})).toBeTruthy();
});
