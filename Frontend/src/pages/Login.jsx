import sneakerImage from '../assets/sneaker.png'
import '../css/Login.css'
import { useState } from 'react'
function Login () {

    /* 
        Why use a separate function to handle the submit and not just action?
        Action would send stuff directly to fastapi... then fastapi returns something
        and then it kills your application, because fastapi returns obejcts and not 
        react web pages LOL.

        so using a function, I can just send data to fastapi via an API request
        and then have react still behave as a "one" page application
    */

    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')    
    const handleSubmit = (e) => { 
        console.log(email)
        console.log(password)
    }
    return (
        <div className="login-content">
            {/* setup the fields, handle the backend stuff later */}
            <form onSubmit={handleSubmit}>
                <img src={sneakerImage}></img>
                <div className="login-inputs">
                    <input value={email} name='email' type='text' placeholder='email' 
                        onChange={(e) => setEmail(e.target.value)}/>
                    <input value={password} name='password' type='password' placeholder='password' 
                        onChange={(e) => setPassword(e.target.value)}/>
                    <button type='submit'> Login </button>
                </div>
            </form>
        </div>
    )
}

export default Login