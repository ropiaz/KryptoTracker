import React from 'react';
import logo from '../../assets/Logo_KryptoTracker.png';
import useLogin from "../../utils/useLogin";
import { Navigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider";

export default function Login() {
    const {
        email,
        setEmail,
        password,
        setPassword,
        errors,
        handleLogin
    } = useLogin();
    const { token } = useStateContext();

    if(token){
        return <Navigate to="/dashboard" />
    }

    return (
        <div className="login-container d-flex">
            <div className="card login-card animated fadeInDown">
                <div className="card-body">
                    <div className="mb-4">
                        <img src={logo} alt="KryptoTracker Logo" className="img-fluid mb-2" />
                        <h3>Login</h3>
                        {errors.length > 0 && (
                            <div className="alert alert-danger">
                                {errors.map((error, index) => (
                                    <div key={index}>{error}</div>
                                ))}
                            </div>
                        )}
                    </div>
                    <form onSubmit={handleLogin} method="post">
                        <div className="mb-3">
                            <input
                                type="email"
                                className="form-control"
                                id="email"
                                placeholder="E-Mail"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                            />
                        </div>
                        <div className="mb-3">
                            <input
                                type="password"
                                className="form-control"
                                id="password"
                                placeholder="Passwort"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                            />
                        </div>
                        <div className="d-flex justify-content-center">
                            <button
                                type="submit"
                                className="login-button"
                                onClick={handleLogin}
                            >
                                Login
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}