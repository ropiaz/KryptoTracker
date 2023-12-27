import React, { useState } from 'react';
import { Navigate, useNavigate } from "react-router-dom";
import axios from "axios";
import { useStateContext } from "../../contexts/ContextProvider";
import logo from '../../assets/Logo_KryptoTracker.png';

export default function Register() {
    const navigate = useNavigate();
    const {setToken, setNotification} = useStateContext();
    const [errors, setErrors] = useState([]);
    const [newUser, setNewUser] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        passwordConfirmed: '',
    });

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const { token } = useStateContext();

    if(token){
        return <Navigate to="/user/dashboard" />
    }

    const fields = [
        { id: 'username', type: 'text', placeholder: 'Username' },
        { id: 'email', type: 'email', placeholder: 'E-Mail' },
        { id: 'first_name', type: 'text', placeholder: 'Vorname' },
        { id: 'last_name', type: 'text', placeholder: 'Nachname' },
        { id: 'password', type: 'password', placeholder: 'Passwort' },
        { id: 'passwordConfirmed', type: 'password', placeholder: 'Passwort wiederholen' },
    ];

    const handleChange = (e) => {
        setNewUser({ ...newUser, [e.target.id]: e.target.value });
    };

    const handleRegister = async (event) => {
        event.preventDefault();

        let newErrors = [];

        const fields = {
            'email': 'E-Mail',
            'username': 'Username',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'password': 'Passwort',
            'passwordConfirmed': 'Passwort wiederholen'
        };

        // Check for empty fields
        for (const [key, value] of Object.entries(newUser)) {
            if (!value) {
                newErrors.push(`Das Feld ${fields[key]} darf nicht leer sein.`);
            }
        }

        if (newUser.password !== newUser.passwordConfirmed) {
            newErrors.push('Passwörter stimmen nicht überein!');
        }

        if (newErrors.length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            await axios.post(`${apiUrl}/register/`, newUser, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {'Content-Type': 'application/json'}
            })
                .then((res) => {
                    setNotification('Registrierung erfolgreich! Weiterleitung...');
                    const token = res.data.token;

                    setToken(token);
                    setNewUser(null);
                    setErrors([]);
                    navigate('/user/dashboard');
                })
                .catch((error) => {
                    if(error.response.status === 500) {
                        setErrors(["Serverfehler bitte später erneut versuchen."]);
                    }

                    if(error.response.status >= 400 && error.response.status < 500) {
                        for (const errorKey in error.response.data) {
                            if(error.response.data[errorKey][0] === "Dieses Feld darf nicht leer sein."){
                                continue;
                            }
                            newErrors.push(error.response.data[errorKey]);
                        }
                        setErrors(newErrors);
                    }
                });
        } catch (err) {
            setErrors(["Fehler beim Registrieren."]);
        }
    };

    return (
        <div className="register-container d-flex">
            <div className="card register-card animated fadeInDown m-1">
                <div className="card-body">
                    <div className="mb-4">
                        <img src={logo} alt="KryptoTracker Logo" className="img-fluid mb-2" />
                        <h3>Register</h3>
                        {errors.length > 0 && (
                            <div className="alert alert-danger">
                                {errors.map((error, index) => (
                                    <div key={index}>{error}</div>
                                ))}
                            </div>
                        )}
                    </div>
                    <form onSubmit={handleRegister}>
                        {fields.map((field) => (
                            <div key={field.id} className="mb-3">
                                <input
                                    type={field.type}
                                    className="form-control"
                                    id={field.id}
                                    placeholder={field.placeholder}
                                    value={newUser[field.id]}
                                    onChange={handleChange}
                                />
                            </div>
                        ))}
                        <div className="d-grid justify-content-center mt-3">
                            <button type="submit" className="register-button">Registrieren</button>
                        </div>
                        <div className="d-grid justify-content-center">
                            <button
                                type="button"
                                className="login-button"
                                onClick={(ev) => {navigate('/login')}}
                            >
                                Bereits registriert? Zum Login
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}