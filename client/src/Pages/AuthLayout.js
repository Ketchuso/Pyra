import { useState } from "react";
import Login from "../components/Login";
import SignUp from "../components/SignUp";

function AuthLayout({ onLogin }){
    const [showLogin, setShowLogin] = useState(true);

    return (
        <div className="auth-layout">
            <h1>Welcome to Pyra!</h1>
            {showLogin ? (
                <>
                    <Login onLogin={onLogin} />
                    <p>
                        Don't have an account?{" "}
                        <button className="button-class" onClick={() => setShowLogin(false)}>
                            Sign Up
                        </button>
                    </p>
                </>
            )
            :(
                <>
                    <SignUp onLogin={onLogin}/>
                    <p>
                        Already have an account?{" "}
                        <button className="button-class" onClick={() => setShowLogin(true)}>
                            Log In
                        </button>
                    </p>
                </>
            )
            }
        </div>
    )
}

export default AuthLayout;