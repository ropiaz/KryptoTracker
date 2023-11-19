import React from 'react';
import { useNavigate, Link } from "react-router-dom";
import { useStateContext } from "../contexts/ContextProvider";
import useAuthUserToken from "../hooks/useAuthUserToken";
import axios from "axios";

export default function Header(){
    const navigate = useNavigate();
    const { setToken, token, setNotification } = useStateContext();
    const { userData, setUserData } = useAuthUserToken(token);

    const onLogout = async (ev) => {
        ev.preventDefault();
        try {
            axios.post('http://localhost:8000/api/logout/', {}, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`
                }
            })
                .then((res) => {
                    setNotification('Logout erfolgreich! Weiterleitung...');
                    setToken(null);
                    setUserData(null);
                    navigate('/');
                })
                .catch((error) => {
                    setToken(null);
                    setUserData(null);
                    navigate('/');
                });
        } catch (error) {
            setToken(null);
            setUserData(null);
            navigate('/');
        }
    }

    // TODO: edit "to" to all Link tags
    return (
        <nav className="navbar navbar-expand-lg bg-body-tertiary">
            <div className="container-fluid">
                <span className="navbar-brand">KryptoTracker</span>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse justify-content-center" id="navbarSupportedContent">
                    <ul className="navbar-nav mb-2 mb-lg-0 ms-auto">
                        <li className="nav-item">
                            <Link className="nav-link" to="/">Home</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to={userData?.username ? `/${userData.username}` : '/'}>Dashboard</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to='/'>Steuerbericht</Link>
                        </li>
                        <li className="nav-item dropdown">
                            <Link to="#" className="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Transaktionen und Staking
                            </Link>
                            <ul className="dropdown-menu">
                                <li><Link className="dropdown-item" to='/'>Historie ansehen</Link></li>
                                <li><Link className="dropdown-item" to='/'>Staking-Rewards</Link></li>
                                <li><hr className="dropdown-divider" /></li>
                                <li><Link className="dropdown-item" to='/'>Transaktion hinzufügen</Link></li>
                                <li><Link className="dropdown-item" to='/'>CSV-Datenimport</Link></li>
                            </ul>
                        </li>
                        <li className="nav-item dropdown">
                            <Link to="#" className="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                Wissen
                            </Link>
                            <ul className="dropdown-menu">
                                <li><Link className="dropdown-item" to='/'>News@KryptoTracker</Link></li>
                                <li><Link className="dropdown-item" to='/'>Rund um Krypto-Steuer</Link></li>
                                <li><hr className="dropdown-divider" /></li>
                                <li><Link className="dropdown-item" to='/'>Something else here</Link></li>
                            </ul>
                        </li>
                    </ul>
                    {userData?.username
                        ?
                        <>
                            <div className="d-flex ms-auto">
                                <div className="dropdown">
                                    <button className="btn btn-light dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                        Hallo, {userData.username}
                                    </button>
                                    <ul className="dropdown-menu">
                                        <li><Link to={`/${userData.username}/settings`} className="dropdown-item">Settings</Link></li>
                                        <li className="dropdown-divider"></li>
                                        <li><Link to="#" className="dropdown-item" onClick={onLogout}>Logout</Link></li>
                                    </ul>
                                </div>
                            </div>
                        </>
                        :
                        <>
                            <div className="d-flex ms-auto">
                                <button type="button"
                                        className="login-button me-2"
                                        onClick={(ev) => {navigate('/login')}}
                                >
                                    Login
                                </button>
                                <button type="button"
                                        className="register-button"
                                        onClick={(ev) => {navigate('/register')}}
                                >
                                    Registrieren
                                </button>
                            </div>
                        </>
                    }
                </div>
            </div>
        </nav>
    );
}