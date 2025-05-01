import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, NavLink, useLocation } from "react-router-dom";

function NavBar({ setUser, user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);

  const currentFilter = params.get("filter") || "news";
  const currentSort = params.get("sort") || "hot";
  const isAuthPage = location.pathname === "/auth";
  const isHomePage = location.pathname === "/" && ["news", "uplifting", null].includes(currentFilter);

  const [isDropdownVisible, setDropdownVisible] = useState(false);
  const [showForm, setShowForm] = useState(false);


  // Redirect to default filter/sort if none is present
  useEffect(() => {
    const hasFilter = params.get("filter");
    const hasSort = params.get("sort");
  
    if (location.pathname === "/" && !hasFilter && !hasSort) {
      navigate("/?sort=hot", { replace: true });
    }
  }, [location, navigate, params]);

  const handleLogoutClick = () => {
    fetch("/logout", { method: "DELETE" }).then((r) => {
      if (r.ok) setUser(null);
    });
  };

  const handleLoginClick = () => {
    navigate("/auth");
  };

  const toggleDropdown = () => setDropdownVisible(!isDropdownVisible);

  const renderDropdownOption = (label, sortType) => (
    <NavLink
      to={`/?sort=${sortType}`}
      className="dropdown-item"
      onClick={() => setDropdownVisible(false)}
      style={{
        color: currentSort === sortType ? 'var(--main-color)' : 'var(--text-color)',
        textDecoration: 'none',
        display: 'block',  // Ensure each option is in its own line
        padding: '8px 16px',  // Some padding for the items
      }}
    >
      {label}
    </NavLink>
  );

  return (
    <nav className="nav-container">
      <NavLink to="/" id="nav-logo">
        <img src="/images/Logo.png" alt="Logo" />
      </NavLink>


      <div className="filters">
        
        <NavLink
          to="/?sort=hot"
          className="nav-text"
        >
          Home
        </NavLink>
        
        {/* Show filter only when on the homepage */}
        {isHomePage && (
          <div className="dropdown">
            <button className="dropbtn" onClick={toggleDropdown}>
              Sort
            </button>
            {isDropdownVisible && (
              <div className="dropdown-content">
                {currentFilter === "news" && renderDropdownOption("Hot", "hot")}
                {currentFilter === "news" && renderDropdownOption("New", "new")}
                {currentFilter === "uplifting" && renderDropdownOption("Hot", "hot")}
                {currentFilter === "uplifting" && renderDropdownOption("New", "new")}
              </div>
            )}
          </div>
        )}

        {user && (
          <NavLink
            to="add-article"
            className="nav-text"
          >
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/></svg>
          </NavLink>
        )}
      </div>

      {/* Right Side: Auth & Settings */}
      <div className="options">
        {user && (
            <NavLink to={`/settings/${user.id}`} id="settings">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3">
                <path d="m370-80-16-128q-13-5-24.5-12T307-235l-119 50L78-375l103-78q-1-7-1-13.5v-27q0-6.5 1-13.5L78-585l110-190 119 50q11-8 23-15t24-12l16-128h220l16 128q13 5 24.5 12t22.5 15l119-50 110 190-103 78q1 7 1 13.5v27q0 6.5-2 13.5l103 78-110 190-118-50q-11 8-23 15t-24 12L590-80H370Zm70-80h79l14-106q31-8 57.5-23.5T639-327l99 41 39-68-86-65q5-14 7-29.5t2-31.5q0-16-2-31.5t-7-29.5l86-65-39-68-99 42q-22-23-48.5-38.5T533-694l-13-106h-79l-14 106q-31 8-57.5 23.5T321-633l-99-41-39 68 86 64q-5 15-7 30t-2 32q0 16 2 31t7 30l-86 65 39 68 99-42q22 23 48.5 38.5T427-266l13 106Zm42-180q58 0 99-41t41-99q0-58-41-99t-99-41q-59 0-99.5 41T342-480q0 58 40.5 99t99.5 41Z" />
              </svg>
            </NavLink>
        )}
        
        {user ? (
          <button id="logout" className="auth button-class" onClick={handleLogoutClick}>
            Logout
          </button>
        ) : (
          !isAuthPage && (
            <button id="login" className="auth button-class" onClick={handleLoginClick}>
              Login
            </button>
          )
        )}
      </div>
    </nav>
  );
}

export default NavBar;
