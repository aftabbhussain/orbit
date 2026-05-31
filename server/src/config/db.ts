import mongoose from "mongoose";
export const connectDB = async () => {
    try{
        const conn = await mongoose.connect(process.env.MONGO_URI as string);
        console.log('mongodb connected successfully');
    }
    catch(error){
        console.error('mongodb connection failed', error);
    }
};