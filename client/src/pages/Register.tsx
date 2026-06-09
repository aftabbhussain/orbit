import { useForm } from "react-hook-form";
import {z} from 'zod'
import { useAuthStore } from "../store/authStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { apiClient } from "../api/client";
import { Link, useNavigate } from "react-router-dom";

const registerSchema = z.object({
    name : z.string().min(1, 'Name is required'),
    email: z.string().email('Invalid email format'),
    password : z.string().min(6, 'Password must be atleast 6 characters')
});

type RegisterFormValues = z.infer<typeof registerSchema>

export default function Register(){
    const setAuth = useAuthStore((state) => state.setAuth);
    const navigate = useNavigate();
    const {register, setError, handleSubmit, formState : {isSubmitting, errors}} = useForm<RegisterFormValues>({
        resolver : zodResolver(registerSchema)
    });

    const onSubmit =  async (data: RegisterFormValues) => {
        try{
            const response = await apiClient.post('/auth/register', data);
            setAuth(response.data, response.data.token)
            navigate('/dashboard');
            
        }
        catch(err : any){
            setError('root', {
                message : err.response?.data?.error || "Registration failed. Please try again later."
            });
        }
        

    }

    return (
        <div className=' flex justify-center items-center min-h-screen bg-gray-50'>
            <div className="p-7 bg-white shadow-md w-full max-w-md rounded-2xl">
                <h2 className="text-center font-bold text-2xl text-gray-500 mb-6">Create Account</h2>
                <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
                    <div>
                        <label className="text-sm font-medium text-gray-700">Name</label>
                        <input 
                            {...register('name')}
                            className="w-full border border-gray-300 rounded focus:ring-1 focus:outline-none focus:ring-blue-500 p-2"
                            placeholder="John Doe"
                         />
                         {errors.name && <span className="text-sm text-red-500 mt-1">{errors.name.message}</span>}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <input 
                        type="email"
                            {...register('email')}
                            className="w-full border border-gray-300 rounded focus:ring-1 focus:outline-none focus:ring-blue-500 p-2"
                            placeholder="user@example.com"
                         />
                         {errors.email && <span className="text-sm text-red-500 mt-1">{errors.email.message}</span>}
                    </div>
                    <div>
                        <label className="text-sm font-medium text-gray-700">Password</label>
                        <input 
                        type="password"
                            {...register('password')}
                            className="w-full border border-gray-300 rounded focus:ring-1 focus:outline-none focus:ring-blue-500 p-2"
                            placeholder="Password"
                         />
                         {errors.password && <span className="text-sm text-red-500 mt-1">{errors.password.message}</span>}
                    </div>
                    {errors.root && <div className="p-3 bg-red-700 rounded-2xl text-white text-sm text-center">{errors.root.message}</div>}
                    <button
                        type="submit"
                        disabled = {isSubmitting}
                        className="bg-blue-500 w-full text-white p-3 rounded-2xl font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors"
                    >{isSubmitting ? `Creating account...` : `Sign Up`}</button>
                </form>
                <p className="mt-4 text-center text-sm text-gray-600">
                    Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Log in</Link>
                </p>
            </div>
        </div>
    )
}