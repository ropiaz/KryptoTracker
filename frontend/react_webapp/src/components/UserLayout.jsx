import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useStateContext } from "../contexts/ContextProvider";
import Footer from "./Footer";
import Header from "./Header";

export default function UserLayout(){
    const { token, notification } = useStateContext();
    if(!token){
        return <Navigate to="/" />
    }

    return (
        <div id="userlayout">
            <Header />
            <main className="min-vh-75">
                <Outlet />
            </main>
            {notification &&
                <div className="notification">
                    {notification}
                </div>
            }
            <Footer />
        </div>
    );
}