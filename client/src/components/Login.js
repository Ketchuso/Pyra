import React, { useState } from "react";
import { useOutletContext, useNavigate } from "react-router-dom";

function Login({ toggle }) {
  const { onLogin } = useOutletContext();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    setErrors([]);
    setIsLoading(true);

    const trimmedUsername = username.trim();
    const trimmedPassword = password.trim();

    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        username: trimmedUsername,
        password: trimmedPassword,
      }),
    }).then((r) => {
      setIsLoading(false);
      if (r.ok) {
        r.json().then((user) =>{ 
          onLogin(user)
          navigate("/?filter=news&sort=hot")
        });
        
      } else {
        r.json().then((err) => {
          const formattedErrors = err.errors || [err.error] || ["Login failed"];
          setErrors(formattedErrors);
        });
      }
    });
  }

  return (
    <div className="form-container">
      <h1 id="login">Login</h1>
      <form onSubmit={handleSubmit}>
        <label className="labels" htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          placeholder="username..."
          autoComplete="off"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label className="labels" htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          placeholder="password..."
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          className="button-class"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? "Loading..." : "Login"}
        </button>

        <div aria-live="polite">
          {errors.map((err, index) => (
            <p key={index}>{err}</p>
          ))}
        </div>
      </form>
      
      {toggle}
    </div>
  );
}

export default Login;
