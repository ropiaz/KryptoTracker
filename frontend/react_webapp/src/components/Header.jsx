import React from 'react';
import { useNavigate, Link } from "react-router-dom";

export default function Header(){
    const navigate = useNavigate();

    // TODO: edit "to" to all Link tags
    // TODO: adjust Header if user is authenticated => remove Login, Register Buttons
    return (
        <nav className="navbar navbar-expand-lg bg-body-tertiary">
            <div className="container-fluid">
                <span className="navbar-brand">KryptoTracker</span>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse justify-content-center" id="navbarSupportedContent">
                    <ul className="navbar-nav mb-2 mb-lg-0">
                        <li className="nav-item">
                            <Link className="nav-link" to="/">Home</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to='/'>Dashboard</Link>
                        </li>
                        <li className="nav-item">
                            <Link className="nav-link" to='/'>Steuerbericht</Link>
                        </li>
                        <li className="nav-item dropdown">
                            <Link className="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false">
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
                            <Link className="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown" aria-expanded="false">
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
                    <div className="d-flex">
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
                </div>
            </div>
        </nav>
    );
}