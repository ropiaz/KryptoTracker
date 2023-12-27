import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { useStateContext } from '../contexts/ContextProvider';

export const getUser = (token) => {
    const { setToken } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchUser = async () => {
        if (!token) return null;
        try {
            const response = await axios.get(`${apiUrl}/user-auth/`, {
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            return response.data.detail;
        } catch (error) {
            setToken(null);
        }
    };

    const { data: userData, error, isLoading, isError } = useQuery(
        ['authUser', token],
        fetchUser,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 60, // Die Daten bleiben für 60 Minuten frisch
            cacheTime: 1000 * 60 * 60, // Cache-Zeit von 60 Minuten
        }
    );

    return { userData, isLoading, isError, error };
};

export const login = () => {
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

            await axios.post(`${apiUrl}/login/`, payload, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {'Content-Type': 'application/json'}
            })
                .then((res) => {
                    setNotification('Login erfolgreich! Weiterleitung...');
                    const token = res.data.token;

                    setToken(token);
                    resetForm();
                    navigate('/user/dashboard');
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