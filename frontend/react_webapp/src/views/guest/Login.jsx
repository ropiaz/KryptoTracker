import React from 'react';
import logo from '../../assets/Logo_KryptoTracker.png';
import useLogin from "../../hooks/useLogin";

export default function Login() {
    const {
        email,
        setEmail,
        password,
        setPassword,
        errorMessage,
        handleLogin
    } = useLogin();

    return (
        <div className="login-container d-flex">
            <div className="card login-card">
                <div className="card-body">
                    <div className="mb-4">
                        <img src={logo} alt="KryptoTracker Logo" className="img-fluid mb-2" />
                        <h3>Login</h3>
                        { errorMessage &&
                            <div className="alert alert-danger alert-dismissible fade show">
                                {errorMessage}
                                <span className="btn btn-sm btn-close" data-bs-dismiss="alert" aria-label="Close"></span>
                            </div>
                        }
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