import React, { type ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import Register from './pages/Register'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import { useAuthStore } from './store/authStore'

const ProtectedRoutes = ({children} : { children: ReactNode }) => {
  const token = useAuthStore((state) => state.token);
  if(!token){
    return <Navigate to = '/login'/>
  }
  return children;
}

const PublicRoute = ({ children }: { children: ReactNode }) => {
  const token = useAuthStore((state) => state.token);
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
};

const App = () => {

  return(
    <BrowserRouter>
      <Routes>
        <Route 
          path='/register' 
          element = {
            <PublicRoute>
                <Register/>
            </PublicRoute>
          } 
        />
        <Route 
          path='/login' 
          element = {
            <PublicRoute>
                <Login/>
            </PublicRoute>
          } 
        />
         <Route 
          path='/dashboard' 
          element = {
            <ProtectedRoutes>
                <Dashboard/>
            </ProtectedRoutes>
          } 
        />
        <Route path='*' element = {<Navigate to = '/register'/>}/>
      </Routes>
      
    </BrowserRouter>
  )
  
}

export default App