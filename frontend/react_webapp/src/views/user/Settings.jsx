import React from "react";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider";
import useAuthUserToken from "../../hooks/useAuthUserToken";

export default function Settings(){
    const navigate = useNavigate();
    const { token, notification, setNotification } = useStateContext();
    const { userData, setUserData } = useAuthUserToken(token); // check if user has valid token

    return (
        <>
            <div className="container mt-2">
                <h2>Settings</h2>
                {userData?.username ? <p>Hallo {userData.username}</p> : "Hallo"}
            </div>
        </>
    );
}
