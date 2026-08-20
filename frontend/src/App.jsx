import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './css/App.css'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Cart from './pages/Cart'

function App() {

  return (
    <>
      <main>
        <Routes>
          <Route path = '/' element = {<Home />}></Route>
          <Route path = '/:username/cart' element = {<Cart />}></Route>
        </Routes>
      </main>
    </>
  )
}

export default App
