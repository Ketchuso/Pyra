import React from "react";
import NavBar from "../components/NavBar";

function ErrorPage(){

    return (
        <>
            <NavBar/>
            <h1 id="error-text"className="center-text">Hey Sorry an Error has occured! Use the Navbar to get back to another page!</h1>
        </>
    )
}

export default ErrorPage