import { Request, Response } from "express"
import { registerSchema, loginSchema } from "../utils/validate"
import { UserModel } from "../models/User";
import { generateToken } from "../utils/jwt";

export const registerUser = async (req : Request, res : Response) => {
    try{
        const validation = registerSchema.safeParse(req.body);
        if(!validation.success){
            return res.status(400).json({
                error : validation.error.issues[0].message
            });
        }
        const {name, email, password} = validation.data;
        const existingUser = await UserModel.findOne({email});
        if(existingUser){
            return res.status(400).json({
                error: "user already exists"
            });
        }
        const newUser = await UserModel.create({name, email, password});
        console.log('user created successfully');
        const token = generateToken(newUser._id.toString());
        return res.status(201).json({
            _id: newUser._id,
            name : newUser.name,
            email : newUser.email,
            token : token
        });
    }
    catch(error: any){
        return res.status(500).json({
            error : error
        })
    }
}   

export const loginUser = async (req: Request, res: Response) => {
    try{
        const validation = loginSchema.safeParse(req.body);
        if(!validation.success){
            return res.status(400).json({
                error: validation.error.issues[0].message
            });
        }
        const {email, password} = validation.data;
        const user : any = await UserModel.findOne({email}).select('+password');
        if(!user){
            return res.status(404).json({
                error : "User doesn't exist"
            });
        }
        const isMatch = await user.comparePassword(password);
        if(!isMatch){
            return res.status(401).json({
                error: "Invalid password"
            });
        }
        console.log('user logged in successfully');
        const token = generateToken(user._id.toString());
        res.status(200).json({
            _id: user._id,
            name : user.name,
            email : user.email,
            token : token
        });
    }
    catch(error){
        return res.status(500).json({
            error : "Internal server error"
        });
    }
}