import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || "hello world";

export const generateToken = (userId : any) : string => {
    return jwt.sign(userId, JWT_SECRET);
}