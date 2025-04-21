import React, { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
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
    <div>
      <NavBar user={user} setUser={setUser}/>
      {/* Passing setUser to the AuthLayout through Outlet */}
      <Outlet context={{ onLogin: setUser }} />
    </div>
  );
}

export default App;
