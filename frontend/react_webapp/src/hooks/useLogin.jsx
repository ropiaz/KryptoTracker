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
                email: email,
                password: password,
            };

            // Check for empty fields
            for (const [key, value] of Object.entries(payload)) {
                if (!value) {
                    newErrors.push(`Das Feld ${key} darf nicht leer sein.`);
                }
            }

            if (newErrors.length > 0) {
                setErrors(newErrors);
                return;
            }

            axios.post('http://localhost:8000/api/login/', payload, {
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

                    setTimeout(() => {
                        navigate(`/${userData.username}`);
                    }, 1250);
                })
                .catch((error) => {
                    for (const errorKey in error.response.data) {
                        console.log(error.response.data[errorKey])
                        newErrors.push(error.response.data[errorKey]);
                    }
                    setErrors(newErrors);
                });
        } catch (err) {
            console.log('Fehler beim Login: ', err);
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