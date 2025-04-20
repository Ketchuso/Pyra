import React from "react";
import { useNavigate, NavLink, useLocation } from "react-router-dom";

function NavBar({ setUser, user }) {
  const navigate = useNavigate();
  const location = useLocation();

  const isAuthPage = location.pathname === "/auth";

  function handleLogoutClick() {
    fetch("/logout", { method: "DELETE" }).then((r) => {
      if (r.ok) {
        setUser(null);
      }
    });
  }

  function handleLoginClick() {
    navigate("/auth");
  }

  if (user) {
    return (
      <>
        <nav>
          <button
            id="logout"
            className="button-class logout"
            variant="outline"
            onClick={handleLogoutClick}
          >
            Logout
          </button>
        </nav>

        <nav className="nav-container">
          <NavLink to={`/settings/${user.id}`} id="settings">
          </NavLink>
          <NavLink to="/?filter=uplifting&sort=hot" className="nav-text">
            Uplifting
          </NavLink>
          <NavLink to="/?filter=news&sort=hot" className="nav-text">
            News
          </NavLink>
        </nav>
      </>
    );
  } else {
    return (
      <>
        <nav>
          {!isAuthPage && (
            <button
              id="login"
              className="button-class login"
              variant="outline"
              onClick={handleLoginClick}
            >
              Login
            </button>
          )}
        </nav>

        <nav className="nav-container">
          <NavLink to="/?filter=uplifting&sort=hot" className="nav-text">
            Uplifting
          </NavLink>
          <NavLink to="/?filter=news&sort=hot" className="nav-text">
            News
          </NavLink>
        </nav>
      </>
    );
  }
}

export default NavBar;
