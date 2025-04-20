import React, { useEffect, useState } from "react";
//import { Outlet } from "react-router-dom";  // Use Outlet to render nested routes
import Home from "../Pages/Home";
import NavBar from "./NavBar";

function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("/check_session", { credentials: "include" }).then((r) => {
      if (r.ok) {
        r.json().then((user) => setUser(user));
      }
    });
  }, []);

  return (
    <>
      <NavBar setUser={setUser} user={user}/>
      <Home/>
    </>
  );
}

export default App;
