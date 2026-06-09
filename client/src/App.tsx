import React from 'react'
import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import Register from './pages/Register'

const App = () => {
  return(
    <BrowserRouter>
      <Routes>
        <Route path='/register' element = {<Register/>} />
        <Route path='/dashboard' element = {<div className="p-8 text-2xl font-bold">Welcome to Orbit Dashboard</div>}/>
        <Route path='*' element = {<Navigate to = '/register'/>}/>
      </Routes>
      
    </BrowserRouter>
  )
  
}

export default App