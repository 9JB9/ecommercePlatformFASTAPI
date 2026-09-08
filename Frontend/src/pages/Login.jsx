
function Login () {

    /* 
        Why use a separate function to handle the submit and not just action?
        Action would send stuff directly to fastapi... then fastapi returns something
        and then it kills your application, because fastapi returns obejcts and not 
        react web pages LOL.

        so using a function, I can just send data to fastapi via an API request
        and then have react still behave as a "one" page application
    */
    const handleSubmit = () => { 
        return
    }
    return (
        <div className="login-content">
            {/* setup the fields, handle the backend stuff later */}
            <form onSubmit={handleSubmit}>
                <img src=""></img>
            </form>
        </div>
    )
}

export default Login