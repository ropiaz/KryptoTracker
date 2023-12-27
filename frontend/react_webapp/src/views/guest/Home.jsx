import React from 'react';
import { useNavigate } from "react-router-dom";
import { login } from "../../hooks/Auth.jsx";
import { useStateContext } from "../../contexts/ContextProvider";

export default function Home(){
    const navigate = useNavigate();
    const {
        email,
        setEmail,
        password,
        setPassword,
        errors,
        handleLogin
    } = login();

    const { token } = useStateContext();

    // TODO: add onClick to /demo/dashboard in discover-button
    return (
        <div className="homepage">
            <div className="banner-image py-4">
                <div className="banner-content">
                    {/*Text Container */}
                    <div className="banner-text">
                        <h1>KryptoTracker</h1>
                        <p>Ihr Begleiter im Krypto-Universum!</p>
                        <p>Mit KryptoTracker behalten Sie mühelos den Überblick über Ihre Kryptowährungen. Verfolgen Sie sämtliche Transaktionen, werten Sie Ihre Gewinne aus und generieren Sie unkompliziert Steuerberichte. Profitieren Sie von unserer spezialisierten Steuerhilfe und bleiben Sie stets bestens informiert. Optimieren Sie Ihr Krypto-Erlebnis mit KryptoTracker!</p>
                        {!token &&
                            <button type="button"
                                    className="discover-button"
                            >
                                Entdecke die Livedemo
                            </button>
                        }
                    </div>
                    {!token &&
                         // Login Container
                        <div className="login-form">
                            <form onSubmit={handleLogin} method="post">
                                <h2>Login</h2>
                                {errors.length > 0 && (
                                    <div className="alert alert-danger">
                                        {errors.map((error, index) => (
                                            <div key={index}>{error}</div>
                                        ))}
                                    </div>
                                )}
                                <div className="form-group mb-3">
                                    <input type="email"
                                           className="form-control"
                                           placeholder="E-Mail"
                                           value={email}
                                           onChange={e => setEmail(e.target.value)}
                                    />
                                </div>
                                <div className="form-group mb-3">
                                    <input type="password"
                                           className="form-control"
                                           placeholder="Passwort"
                                           value={password}
                                           onChange={e => setPassword(e.target.value)}
                                    />
                                </div>
                                <div className="form-group mb-2 text-center">
                                    <button type="submit" className="login-button">Login</button>
                                </div>
                                <div className="form-group mb-2 text-center">
                                    <span>Oder</span>
                                </div>
                                <div className="form-group text-center">
                                    <button type="button"
                                            className="register-button"
                                            onClick={(ev) => navigate('/register')}
                                    >
                                        Registrieren
                                    </button>
                                </div>
                            </form>
                        </div>
                    }
                </div>
            </div>
            {/* Service Section */}
            <div className="container service-container">
                <section className="service">
                    <div className="service-description">
                        <h2>Portfolio und Assetverwaltung</h2>
                        <ul>
                            <li>Verfolge die Leistung deines Portfolios in einem Dashboard, einschließlich Gesamtwert, Gewinn/Verlust und Vermögensverteilung.</li>
                            <li>Überwache, analysiere und optimiere deine Krypto Investitionen und Holdings wie ein Profi.</li>
                        </ul>
                    </div>
                    <div className="service-image" id="service-image1"></div>
                </section>
                <section className="service">
                    <div className="service-description">
                        <h2>Transaktionen und Staking</h2>
                        <ul>
                            <li>Erhalte eine komplette Übersicht deiner Transaktionen aus unterstützten Wallets und Börsen sowie automatischer Kategorisierung.</li>
                            <li>Filteroptionen liefern deine gewünschten Transaktionen.</li>
                            <li>Importiere deine Trades mithilfe des Datenimports oder API, um ein klares Bild deiner Aktivitäten in allen Depots zu bekommen.</li>
                        </ul>
                    </div>
                    <div className="service-image" id="service-image2"></div>
                </section>
                <section className="service">
                    <div className="service-description">
                        <h2>Krypto-Steuerhilfe</h2>
                        <ul>
                            <li>Erleichtert die Nachweispflicht für deine Steuerbehörde</li>
                            <li>Aufschlüsselung der Staking-, Lending- und Mining-Transaktionen</li>
                            <li>Kapitalgewinne aus langfristige und kurzfristige Gewinne und Verluste</li>
                            <li>Unsere Steuerberichte enthalten klare Erklärungen für deine Steuerbehörden</li>
                        </ul>
                    </div>
                    <div className="service-image" id="service-image3"></div>
                </section>
                <section className="service">
                    <div className="service-description">
                        <h2 className="mb-3 text-center">Warum Krypto-Tracker nutzen?</h2>
                        <div className="service-image" id="service-image4"></div>
                        <p className="mt-2">
                            Der Markt für Kryptowährungen ist sehr volatil und kann sowohl für Neulinge als auch für erfahrene Trader eine Herausforderung darstellen. KryptoTracker bietet eine wertvolle Lösung, indem es den Prozess der Verfolgung und Verwaltung digitaler Vermögenswerte vereinfacht. Dank der integrierten Steuerhilfe werden alle Transaktionen, Gewinne und Verluste für Sie dokumentiert.
                        </p>
                    </div>
                </section>
            </div>
        </div>
    );
}