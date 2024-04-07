import React, {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import { getUser } from "../../hooks/Auth.jsx";
import axios from "axios";

export default function Settings(){
    const navigate = useNavigate();
    const { token, setNotification } = useStateContext();
    const { userData } = getUser(token);
    const [editUser, setEditUser] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        passwordConfirmed: '',
    });

    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    useEffect(() => {
        if (userData) {
            setEditUser({
                first_name: userData.first_name || '',
                last_name: userData.last_name || '',
                username: userData.username || '',
                email: userData.email || '',
                password: '',
                passwordConfirmed: '',
            });
        }
    }, [userData]);

    const [errors, setErrors] = useState([]);

    const handleEdit = async (event) => {
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
        for (const [key, value] of Object.entries(editUser)) {
            if (!value) {
                newErrors.push(`Das Feld ${fields[key]} darf nicht leer sein.`);
            }
        }

        if (editUser.password !== editUser.passwordConfirmed) {
            newErrors.push('Passwörter stimmen nicht überein!');
        }

        if (newErrors.length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            await axios.put(`${apiUrl}/user-edit/${token}`, editUser, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`
                }
            })
                .then((res) => {
                    setNotification('Aktualisierung erfolgreich! Weiterleitung...');
                    setErrors([]);
                    navigate('/user/settings');
                    window.location.reload();
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
            setErrors(["Fehler beim Aktualisieren."]);
        }
    };

    return (
        <>
            <div className="container mt-3 mb-3 fadeInDown animated">
                <h2>Settings</h2>
                <div className="card h-100">
                    <div className="card-body">
                        <form onSubmit={handleEdit}>
                            <h2 className="mb-3">Meine Daten</h2>
                            {errors.length > 0 && (
                                <div className="alert alert-danger">
                                    {errors.map((error, index) => (
                                        <div key={index}>{error}</div>
                                    ))}
                                </div>
                            )}
                            <small className="required-text">* erforderlich</small>
                            <div className="form-floating mb-3">
                                <input type="text"
                                       className="form-control"
                                       id="firstName"
                                       name="firstName"
                                       placeholder="Vorname"
                                       value={editUser.first_name}
                                       onChange={e => setEditUser({...editUser, first_name: e.target.value})}
                                />
                                <label htmlFor="firstName">Vorname</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="text"
                                       className="form-control"
                                       id="lastName"
                                       name="lastName"
                                       placeholder="Nachname"
                                       value={editUser.last_name}
                                       onChange={e => setEditUser({...editUser, last_name: e.target.value})}

                                />
                                <label htmlFor="lastName">Nachname</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="text"
                                       className="form-control"
                                       id="username"
                                       name="username"
                                       placeholder="Benutzername"
                                       value={editUser.username}
                                       onChange={e => setEditUser({...editUser, username: e.target.value})}
                                />
                                <label htmlFor="username">Username</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="email"
                                       className="form-control"
                                       id="email"
                                       name="email"
                                       placeholder="name@example.com"
                                       value={editUser.email}
                                       onChange={e => setEditUser({...editUser, email: e.target.value})}
                                />
                                <label htmlFor="email">E-Mail</label>
                            </div>
                            <div className="form-floating mb-3">
                                <input type="password"
                                       className="form-control"
                                       id="password"
                                       name="password"
                                       placeholder="Passwort*"
                                       value={editUser.password}
                                       onChange={e => setEditUser({...editUser, password: e.target.value})}
                                />
                                <label htmlFor="password">Passwort*</label>
                            </div>
                            <div className="form-floating mb-3">
                                <input type="password"
                                       className="form-control"
                                       id="passwordConfirmed"
                                       name="passwordConfirmed"
                                       placeholder="Passwort wiederholen*"
                                       value={editUser.passwordConfirmed}
                                       onChange={e => setEditUser({...editUser, passwordConfirmed: e.target.value})}
                                />
                                <label htmlFor="passwordConfirmed">Passwort wiederholen*</label>
                            </div>

                            <div className="mt-3">
                                <button type="submit" className="btn btn-primary">Aktualisieren</button>
                            </div>
                        </form>

                    </div>
                </div>
            </div>
        </>
    );
}
