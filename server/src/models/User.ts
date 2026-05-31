import mongoose, {Document} from "mongoose";
import bcrypt from 'bcrypt';

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    email :{
        type: String,
        required : true,
        unique : true
    },
    password : {
        type : String,
        required : true,
        select : false
    }
}, {timestamps : true});

userSchema.pre('save', async function(){
    if(!this.isModified('password')) return;
    const hashedPassword = await bcrypt.hash(this.password, 10);
    this.password = hashedPassword;
    
});

userSchema.methods.comparePassword = async function(userPassword: string){
    return await bcrypt.compare(userPassword, this.password);
}

export const UserModel = mongoose.model('User', userSchema);

