import express, {Request, Response, Application} from 'express'
import { connectDB } from './config/db';
import dotenv from 'dotenv';
import cors from 'cors';

dotenv.config();

connectDB();

const PORT = process.env.PORT || 3000;
const app : Application = express();

app.use(cors());
app.use(express.json());

app.get('/health', (req : Request, res : Response) => {
    res.status(200).json({
        status : 'server running'
    });
})

app.listen(PORT, () => {
    console.log(`server running at port ${PORT}`);
});