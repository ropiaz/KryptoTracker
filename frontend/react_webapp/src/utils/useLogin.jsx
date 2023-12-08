import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStateContext } from '../contexts/ContextProvider';
import axios from 'axios';

export default function useLogin(){
    const { setToken, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState([]);

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const resetForm = () => {
        setEmail('');
        setPassword('');
        setErrors([]);
    };

    const handleLogin = async (event) => {
        event.preventDefault();

        try {
            let newErrors = [];

            const payload = {
                'email': email,
                'password': password,
            };

            const fields = {
                'email': 'E-Mail',
                'password': 'Passwort',
            };

            // Check for empty fields
            for (const [key, value] of Object.entries(payload)) {
                if (!value) {
                    newErrors.push(`Das Feld ${fields[key]} darf nicht leer sein.`);
                }
            }

            if (newErrors.length > 0) {
                setErrors(newErrors);
                return;
            }

            axios.post(`${apiUrl}/login/`, payload, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {'Content-Type': 'application/json'}
            })
                .then((res) => {
                    setNotification('Login erfolgreich! Weiterleitung...');
                    const userData = res.data.detail;
                    const token = res.data.token;

                    setToken(token);
                    resetForm();

                    navigate(`/${userData.username}`);
                })
                .catch((error) => {
                    if(error.response.status === 500) {
                        setErrors(["Serverfehler bitte später erneut versuchen."]);
                    }

                    if(error.response.status >= 400 && error.response.status < 500) {
                        for (const errorKey in error.response.data) {
                            newErrors.push(error.response.data[errorKey]);
                        }
                        setErrors(newErrors);
                    }
                });
        } catch (err) {
            setErrors(["Fehler beim Login."]);
        }
    };

    return {
        email,
        setEmail,
        password,
        setPassword,
        errors,
        handleLogin
    };
};