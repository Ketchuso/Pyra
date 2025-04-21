import React, { useState } from "react";

function SignUp({ onLogin, toggle }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirmation, setPasswordConfirmation] = useState('');
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    setErrors([]);
    setIsLoading(true);

    const trimmedUsername = username.trim();
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const trimmedPasswordConfirmation = passwordConfirmation.trim();

    fetch("/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: trimmedUsername,
        email: trimmedEmail,
        password: trimmedPassword,
        password_confirmation: trimmedPasswordConfirmation,
      }),
    })
      .then((response) => {
        setIsLoading(false);
        return response.json();
      })
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          onLogin(data);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Something went wrong.");
      });
  }

  return (
    <div className="form-container">
      <h1>Sign Up</h1>
      <form onSubmit={handleSubmit}>
        <label className="labels" htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          autoComplete="off"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <label className="labels" htmlFor="email">Email</label>
        <input
          type="text"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="off"
        />

        <label className="labels" htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
        />

        <label className="labels" htmlFor="password_confirmation">Password Confirmation</label>
        <input
          type="password"
          id="password_confirmation"
          value={passwordConfirmation}
          onChange={(e) => setPasswordConfirmation(e.target.value)}
          autoComplete="current-password"
        />

        <button className="button-class" type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Sign Up"}
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

export default SignUp;
