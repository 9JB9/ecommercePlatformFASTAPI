import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './css/App.css'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Cart from './pages/Cart'
import Login from './pages/Login'
import Signup from './pages/Signup'

function App() {

  return (
    <>
      <main>
        <Routes>
          <Route path = '/' element = {<Home />}></Route>
          <Route path = '/:username/cart' element = {<Cart />}></Route>
          <Route path = '/login' element = {<Login />}/>
          <Route path = '/signup' element = {<Signup />}/>
        </Routes>
      </main>
    </>
  )
}

export default App
