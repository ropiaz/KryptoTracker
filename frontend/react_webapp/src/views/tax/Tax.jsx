import React from "react";
import {useNavigate} from "react-router-dom";
import {useStateContext} from "../../contexts/ContextProvider.jsx";
import axios from "axios";

export default function Tax(){
    const navigate = useNavigate();
    const { token, setNotification } = useStateContext();
    // TODO: Check if user is authenticated

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    return (
        <div className="container mt-2 mb-2">
            <h2>Steuern</h2>
        </div>
    );
}
