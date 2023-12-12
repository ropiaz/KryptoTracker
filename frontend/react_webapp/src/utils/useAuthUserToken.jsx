import { useEffect, useState } from "react";
import { useStateContext } from "../contexts/ContextProvider";
import axios from "axios";

// check if the given token is valid and returns authenticated user
const useAuthUserToken = (token) => {
    const [userData, setUserData] = useState(null);
    const { setToken} = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    useEffect(() => {
        if (token) {
            axios.get(`${apiUrl}/user-auth/`, {
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            })
                .then((response) => {
                    if (response.status === 200) {
                        setUserData(response.data.detail);
                    }
                })
                .catch((error) => {
                    setToken(null);
                    setUserData(null);
                });
        }
    }, [token]);

    return {
        userData,
        setUserData
    };
}

export default useAuthUserToken;