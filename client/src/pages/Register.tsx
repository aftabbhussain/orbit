import { useForm } from "react-hook-form";
import { useNavigate, Link } from "react-router-dom";
import {z} from 'zod';
import { useAuthStore } from "../store/authStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { apiClient } from "../api/client";
const registerSchema = z.object({
    name: z.string().min(1, 'Name is required'),
    email: z.string().email('Invalid email'),
    password: z.string().min(6, 'Password should be atleast 6 characters')
})
type RegisterFormValues = z.infer<typeof registerSchema>

export default function Register(){
    const setAuth = useAuthStore((state) => state.setAuth);
    const navigate = useNavigate();
    const {register, handleSubmit, setError, formState : {errors, isSubmitting}} = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema)
    });
    const onSubmit = async (data: RegisterFormValues) => {
        try{
            const response = await apiClient.post('/auth/register', data);
            setAuth(response.data, response.data.token);
            navigate('/register');
        }
        catch(error: any){
            setError("root", {
                message: error.response?.data?.error || "Registration failed, please try agian"
            });
        }
    }
    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50">
            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md border border-gray-100">
                <h2 className="text-2xl font-bold text-center text-gray-900 mb-6">Create an Account</h2>
                
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                        <input 
                            {...register("name")} 
                            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            placeholder="John Doe"
                        />
                        {errors.name && <span className="text-red-500 text-sm mt-1">{errors.name.message}</span>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input 
                            type="email" 
                            {...register("email")} 
                            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            placeholder="you@example.com"
                        />
                        {errors.email && <span className="text-red-500 text-sm mt-1">{errors.email.message}</span>}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                        <input 
                            type="password" 
                            {...register("password")} 
                            className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                            placeholder="••••••••"
                        />
                        {errors.password && <span className="text-red-500 text-sm mt-1">{errors.password.message}</span>}
                    </div>

                    {errors.root && (
                        <div className="p-3 bg-red-50 text-red-700 rounded text-sm text-center">
                            {errors.root.message}
                        </div>
                    )}

                    <button 
                        type="submit" 
                        disabled={isSubmitting}
                        className="w-full bg-blue-600 text-white font-medium p-2 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                        {isSubmitting ? "Creating account..." : "Sign Up"}
                    </button>
                </form>

                <p className="mt-4 text-center text-sm text-gray-600">
                    Already have an account? <Link to="/login" className="text-blue-600 hover:underline">Log in</Link>
                </p>
            </div>
        </div>
    );
};
