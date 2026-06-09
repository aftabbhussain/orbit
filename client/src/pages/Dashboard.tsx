import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore"

export default function Dashboard(){
    const {user, logout} = useAuthStore();
    const navigate = useNavigate();
    const handleLogout = () => {
        logout();
        navigate('/login');
    }
    return(
        <div className="min-h-screen bg-gray-50 flex justify-center items-center">
            <div className="p-6 min-w-2xl bg-white rounded-2xl mx-auto shadow-lg border border-gray-200">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-700">Orbit Dashboard</h1>
                    <button 
                    onClick={handleLogout}
                    className="text-sm bg-gray-100 text-gray-700 px-4 py-2 rounded hover:bg-gray-200">
                        Log Out
                    </button>
                </div>
                <div className="bg-blue-50 text-blue-800 p-4 rounded">
                    Welcome back, <span className="font-bold">{user?.name || "User"}</span>
                </div>
            </div>
        </div>
    )
}