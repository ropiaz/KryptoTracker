import React, { useState } from 'react';
import {Navigate, useNavigate} from "react-router-dom";
import {useStateContext} from "../../contexts/ContextProvider";
import axios from "axios";
import logo from '../../assets/Logo_KryptoTracker.png';

export default function Register() {
    const navigate = useNavigate();
    const {setToken, setNotification} = useStateContext();
    const [errors, setErrors] = useState([]);
    const [user, setUser] = useState({
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
        return <Navigate to="/dashboard" />
    }

    const handleRegister = async (event) => {
        event.preventDefault();

        try {
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
            for (const [key, value] of Object.entries(user)) {
                if (!value) {
                    newErrors.push(`Das Feld ${fields[key]} darf nicht leer sein.`);
                }
            }

            if (user.password !== user.passwordConfirmed) {
                newErrors.push('Passwörter stimmen nicht überein!');
            }

            if (newErrors.length > 0) {
                setErrors(newErrors);
                return;
            }

            // request to backend
            axios.post(`${apiUrl}/register/`, user, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {'Content-Type': 'application/json'}
            })
                .then((res) => {
                    setNotification('Registrierung erfolgreich! Weiterleitung...');
                    const userData = res.data.detail;
                    const token = res.data.token;

                    setToken(token);
                    setUser(null);
                    setErrors([]);

                    navigate(`/${userData.username}`);
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
                        <div className="mb-3">
                            <input
                                type="text"
                                className="form-control"
                                id="username"
                                placeholder="Username"
                                value={user.username}
                                onChange={e => setUser({...user, username: e.target.value})}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="email"
                                className="form-control"
                                id="email"
                                placeholder="E-Mail"
                                value={user.email}
                                onChange={e => setUser({...user, email: e.target.value})}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="text"
                                className="form-control"
                                id="firstname"
                                placeholder="Vorname"
                                value={user.first_name}
                                onChange={e => setUser({...user, first_name: e.target.value})}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="text"
                                className="form-control"
                                id="lastname"
                                placeholder="Nachname"
                                value={user.last_name}
                                onChange={e => setUser({...user, last_name: e.target.value})}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="password"
                                className="form-control"
                                id="password"
                                placeholder="Passwort"
                                value={user.password}
                                onChange={e => setUser({...user, password: e.target.value})}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="password"
                                className="form-control"
                                id="passwordConfirmed"
                                placeholder="Passwort wiederholen"
                                value={user.passwordConfirmed}
                                onChange={e => setUser({...user, passwordConfirmed: e.target.value})}
                            />
                        </div>
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