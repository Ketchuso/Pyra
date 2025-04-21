import { useState } from "react";
import Login from "../components/Login";
import SignUp from "../components/SignUp";

function AuthLayout({ onLogin, setUser }) {
  const [showLogin, setShowLogin] = useState(true);

  const toggle = showLogin ? (
    <p>
      Don't have an account?{" "}
      <button className="button-class" onClick={() => setShowLogin(false)}>
        Sign Up
      </button>
    </p>
  ) : (
    <p>
      Already have an account?{" "}
      <button className="button-class" onClick={() => setShowLogin(true)}>
        Log In
      </button>
    </p>
  );

  return (
    <div className="auth-layout">
      <h1>Welcome to Pyra!</h1>
      {showLogin ? (
        <Login onLogin={onLogin} toggle={toggle} />
      ) : (
        <SignUp onLogin={onLogin} setUser={setUser} toggle={toggle} />
      )}
    </div>
  );
}

export default AuthLayout;
