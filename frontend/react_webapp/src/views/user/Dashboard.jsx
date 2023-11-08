import React from "react";
import {useNavigate} from "react-router-dom";
import {useStateContext} from "../../contexts/ContextProvider";

export default function Dashboard(){
    const navigate = useNavigate();
    const {user, setUser, token, setToken} = useStateContext();

    // TODO: Check if user is authenticated

    return (
        <div className="container mt-5">
            {user?.username} Du bist eingeloggt!
        </div>
    );
}
