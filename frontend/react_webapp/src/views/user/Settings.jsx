import React, {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider";
import useAuthUserToken from "../../utils/useAuthUserToken";
import axios from "axios";

export default function Settings(){
    const navigate = useNavigate();
    const { token, notification, setNotification } = useStateContext();
    const { userData, setUserData } = useAuthUserToken(token); // check if user has valid token
    const [user, setUser] = useState({
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        passwordConfirmed: '',
    });

    useEffect(() => {
        if (userData) {
            setUser({
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

            axios.put('http://localhost:8000/api/user-edit/', user, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {'Content-Type': 'application/json'}

            })
                .then((res) => {
                    setNotification('Aktualisierung erfolgreich! Weiterleitung...');
                    const userData = res.data.detail;
                    // const token = res.data.token;

                    // setToken(token);

                    // reset form and errors
                    // setUser(null);
                    // setErrors([]);

                    navigate(`/${userData.username}/settings`);
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
            <div className="container mt-2 mb-2">
                <h2>Settings</h2>
                <div className="card animated fadeInDown h-100">
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
                                       id="floatingInput1"
                                       placeholder="Vorname"
                                       value={user.first_name}
                                       onChange={e => setUser({...user, first_name: e.target.value})}
                                />
                                <label htmlFor="floatingInput1">Vorname</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="text"
                                       className="form-control"
                                       id="floatingInput2"
                                       placeholder="Nachname"
                                       value={user.last_name}
                                       onChange={e => setUser({...user, last_name: e.target.value})}

                                />
                                <label htmlFor="floatingInput2">Nachname</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="text"
                                       className="form-control"
                                       id="floatingInput3"
                                       placeholder="Benutzername"
                                       value={user.username}
                                       onChange={e => setUser({...user, username: e.target.value})}
                                />
                                <label htmlFor="floatingInput3">Username</label>
                            </div>

                            <div className="form-floating mb-3">
                                <input type="email"
                                       className="form-control"
                                       id="floatingInput4"
                                       placeholder="name@example.com"
                                       value={user.email}
                                       onChange={e => setUser({...user, email: e.target.value})}
                                />
                                <label htmlFor="floatingInput4">E-Mail</label>
                            </div>
                            <div className="form-floating mb-3">
                                <input type="password"
                                       className="form-control"
                                       id="floatingInput5"
                                       placeholder="Passwort*"
                                       value={user.password}
                                       onChange={e => setUser({...user, password: e.target.value})}
                                />
                                <label htmlFor="floatingInput5">Passwort*</label>
                            </div>
                            <div className="form-floating mb-3">
                                <input type="password"
                                       className="form-control"
                                       id="floatingInput6"
                                       placeholder="Passwort wiederholen*"
                                       value={user.passwordConfirmed}
                                       onChange={e => setUser({...user, passwordConfirmed: e.target.value})}
                                />
                                <label htmlFor="floatingInput6">Passwort wiederholen*</label>
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
