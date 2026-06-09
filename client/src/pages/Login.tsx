import {z} from 'zod'
import { useAuthStore } from '../store/authStore'
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';


const loginSchema = z.object({
    email: z.string().email('Email is required'),
    password : z.string().min(6, 'Password should be atleast 6 characters')
});
type LoginFormValues = z.infer<typeof loginSchema>
export default function(){
    const navigate = useNavigate();
    const {register, setError, handleSubmit, formState : {isSubmitting, errors}} = useForm<LoginFormValues>({
        resolver : zodResolver(loginSchema)
    });
    const {setAuth} = useAuthStore();
    const onSubmit = async (data: LoginFormValues) => {
        try{
            const response = await apiClient.post('/auth/login', data);
            setAuth(response.data, response.data.token);
            navigate('/dashboard');
        }
        catch(err : any){
            setError('root', {
                message : err.response?.data?.error || "Login failed, please try again later"
            });
        }
    }

    return(
        <div className='bg-gray-50 min-h-screen flex justify-center items-center'>
            <div className='p-7 max-w-md w-full bg-white shadow-md rounded-2xl'>
                <h2 className='text-center font-bold text-gray-500 text-2xl mb-6'>Login Account</h2>
                <form className='space-y-4' onSubmit={handleSubmit(onSubmit)}>
                    <div>
                        <label className='text-sm font-medium text-gray-500'>Email</label>
                        <input 
                            {...register('email')}
                            className= 'w-full border border-gray-300 rounded focus:ring-1 focus:outline-none focus:ring-blue-500 p-2'
                            placeholder='John Doe'
                         />
                         {errors.email && <span className="text-sm text-red-500 mt-1">{errors.email.message}</span>}
                    </div>
                    <div>
                        <label className='text-sm font-medium text-gray-500'>Password</label>
                        <input 
                            {...register('password')}
                            type='password'
                            className= 'w-full border border-gray-300 rounded focus:ring-1 focus:outline-none focus:ring-blue-500 p-2'
                            placeholder='Password'
                         />
                         {errors.password && <span className="text-sm text-red-500 mt-1">{errors.password.message}</span>}
                    </div>
                    {errors.root && <div className="p-3 bg-red-700 rounded-2xl text-white text-sm text-center">{errors.root.message}</div>}
                    <button
                        type="submit"
                        disabled = {isSubmitting}
                        className="bg-blue-500 w-full text-white p-3 rounded-2xl font-medium hover:bg-blue-600 disabled:opacity-50 transition-colors"
                    >{isSubmitting ? `Logging in...` : `Login`}</button>
                </form>
                <p className="mt-4 text-center text-sm text-gray-600">
                    Don't have an account? <Link to="/register" className="text-blue-600 hover:underline">Sign up</Link>
                </p>

            </div>
        </div>
    )
}