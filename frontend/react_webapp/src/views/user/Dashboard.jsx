import React from "react";
import {useNavigate} from "react-router-dom";
import {useStateContext} from "../../contexts/ContextProvider";
import useAuthUserToken from "../../utils/useAuthUserToken.jsx";
import axios from "axios";

export default function Dashboard(){
    const navigate = useNavigate();
    const { token, setNotification } = useStateContext();
    const { userData, setUserData } = useAuthUserToken(token);
    // TODO: Check if user is authenticated

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    return (
        <div className="container mt-5">
            Du bist eingeloggt!
        </div>
    );
}
