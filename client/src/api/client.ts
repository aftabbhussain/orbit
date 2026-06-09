import axios from "axios";
import { useAuthStore } from "../store/authStore";

export const apiClient = axios.create({
    baseURL: 'http://localhost:4000/api'
})
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if(token){
        config.headers.Authorization = `Bearer ${token}`
    }
    return config;
}, 
(error) => {
    return Promise.reject(error)
});