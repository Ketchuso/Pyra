import React from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./components/App";
import Home from "./Pages/Home";
import AuthLayout from "./Pages/AuthLayout";  // Import AuthLayout

import "./index.css";
import Settings from "./Pages/Settings";
import ArticlePage from "./Pages/ArticlePage";
import AddArticle from "./Pages/AddArticle";
import ErrorPage from "./Pages/ErrorPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage/>,
    children: [
      { path: "/", element: <Home /> },
      { path: "/auth", element: <AuthLayout /> },
      { path: "/settings/:id", element: <Settings /> },
      { path: "/article/:id", element:<ArticlePage/> },
      { path: "/add-article", element:<AddArticle/>}
    ],
  },
]);



const container = document.getElementById("root");
const root = createRoot(container);
root.render(<RouterProvider router={router} />);
