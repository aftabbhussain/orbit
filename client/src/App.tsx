import React from 'react'
import { BrowserRouter, Routes, Route , Navigate} from 'react-router-dom'
import Register from './pages/Register'

const App = () => {
  return(
    <BrowserRouter>
      <Routes>
        <Route path='/register' element = {<Register/>} />
      </Routes>
    </BrowserRouter>
  )
  
}

export default App