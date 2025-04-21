import React, { useEffect } from "react";
import { useNavigate, NavLink, useLocation } from "react-router-dom";

function NavBar({ setUser, user }) {
  const navigate = useNavigate();
  const location = useLocation();
  

  const params = new URLSearchParams(location.search);
  const currentFilter = params.get("filter") || "news";
  const isAuthPage = location.pathname === "/auth";

  useEffect(() => {
    if (location.pathname === "/" && !params.get("filter")) {
      navigate("/?filter=news&sort=hot", { replace: true });
    }
  }, [location, navigate, params]);


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

  return (
    <>
      <nav className="nav-container">
      
        <NavLink to={`/`} id="nav-logo">
            Pyra
        </NavLink>

        <div>
          <NavLink
            to="/?filter=uplifting&sort=hot"
            className="nav-text"
            style={{
              color: currentFilter === "uplifting" ? "var(--main-color)" : "var(--text-color)",
              textDecoration: "none",
            }}
          >
            Uplifting
          </NavLink>

          <NavLink
            to="/?filter=news&sort=hot"
            className="nav-text"
            style={{
              color: currentFilter === "news" ? "var(--main-color)" : "var(--text-color)",
              textDecoration: "none",
            }}
          >
            News
          </NavLink>
        </div>
        
        <div>
        {user && (
          <NavLink to={`/settings/${user.id}`} id="settings">
            Settings
          </NavLink>
        )}

        {user ? (
          <button
            id="logout"
            className="auth button-class"
            variant="outline"
            onClick={handleLogoutClick}
          >
            Logout
          </button>
        ) : (
          !isAuthPage && (
            <button
              id="login"
              className="auth button-class"
              variant="outline"
              onClick={handleLoginClick}
            >
              Login
            </button>
          )
        )}
        </div>

      </nav>
    </>
  );
}

export default NavBar;
