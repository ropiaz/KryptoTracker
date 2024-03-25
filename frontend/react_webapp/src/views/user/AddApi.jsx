import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import axios from "axios";

export default function AddApi(){
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [exchange, setExchange] = useState('Kraken');
    const [apiKey, setApiKey] = useState(null);
    const [apiSec, setApiSec] = useState(null);

    const handleExchangeChange = (ev) => {
        setExchange(ev.target.value);
    };

    const handleSubmitAPIKeys = async (ev) => {
        ev.preventDefault();

        if (exchange === 'Kraken' && (!apiKey || !apiSec)) {
            setErrors(["Bitte geben Sie ihren API-Key und API-Secret ein."]);
            return;
        }

        if (exchange !== 'Kraken' && !apiKey) {
            setErrors(["Bitte geben Sie ihren API-Key ein."]);
            return;
        }

        try {
            const formData = {
                'exchange': exchange,
                'apiKey': apiKey,
                'apiSec': apiSec
            }
            const response = await axios.post(`${apiUrl}/exchange-api/`, formData, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                }
            });

            if(response.status === 202){
                setErrors([response.data.message]);
            }

            if(response.status === 200){
                setErrors([]);
                setExchange('Kraken');
                setApiKey(null);
                setApiSec(null);
                setNotification("API-Schlüssel erfolgreich hinzugefügt.");
                navigate('/user/api/add');
                window.location.reload();
            }

        } catch (error) {
            setErrors([error.response.data.error]);
            console.error("Fehler beim Senden der API-Schlüssel", error);
        }
    };

    useEffect(() => {
        setApiKey(null);
        setApiSec(null);
    }, [exchange]);

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Eingabe von API-Schlüsseln zur automatischen Datenabfrage</h2>

                    <div className="alert alert-warning alert-dismissible fade show" role="alert">
                        <strong>Achtung:</strong> Aktuell ist nur die API-Anbindung zur Kraken Börse möglich!
                        <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>

                    <div className="mb-3">
                        <p className="card-text">
                            Bei der automatischen Datenabfrage wird <strong>einmal</strong> täglich die Börse nach
                            Aktualisierungen untersucht.<br/>
                            Hierbei werden neue Transaktionen und Portfoliobestände überführt.<br/>
                            Achte darauf, dass der API-Schlüssel alle notwendigen Berechtigung hat - bei Kraken: <br/>
                        </p>
                        <ul>
                            <li>Query Funds</li>
                            <li>Deposit Funds</li>
                            <li>Withdraw Funds</li>
                            <li>Query open orders & trades</li>
                            <li>Query closed orders & trades</li>
                            <li>Query ledger entries</li>
                        </ul>
                    </div>

                    {errors.length > 0 && (
                        <div className="alert alert-danger">
                            {errors.map((error, index) => (
                                <div key={index}>{error}</div>
                            ))}
                        </div>
                    )}

                    <div className="mb-3 row">
                        <label htmlFor="exchange" className="col-sm-3 col-form-label">
                            Wähle eine Börse aus:<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-8">
                            <select name="exchange" className="form-select" style={{width: 'auto'}}
                                    onChange={handleExchangeChange} value={exchange}>
                                <option value="Kraken">Kraken</option>
                                <option value="Binance" disabled>Binance</option>
                                <option value="Bitpanda" disabled>Bitpanda</option>
                                <option value="Coinbase" disabled>Coinbase</option>
                            </select>
                        </div>
                    </div>

                    <form onSubmit={handleSubmitAPIKeys} method="post" key={exchange}>
                        {exchange === 'Kraken' ? (
                            <>
                                <div className="mb-3 row">
                                    <label htmlFor="apiKey" className="col-sm-3 col-form-label">
                                        API-Key:<span style={{color: "red"}}>*</span>
                                    </label>
                                    <div className="col-sm-8">
                                        <input type="text"
                                               placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                               id="apiKey"
                                               name="apiKey"
                                               className="form-control"
                                               onChange={e => setApiKey(e.target.value)}
                                               required
                                        />
                                    </div>
                                </div>

                                <div className="mb-3 row">
                                    <label htmlFor="apiSec" className="col-sm-3 col-form-label">
                                        API-Sec:<span style={{color: "red"}}>*</span>
                                    </label>
                                    <div className="col-sm-8">
                                        <input type="text"
                                               placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                               id="apiSec"
                                               name="apiSec"
                                               className="form-control"
                                               onChange={e => setApiSec(e.target.value)}
                                               required
                                        />
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="mb-3 row">
                                <label htmlFor="apiKey" className="col-sm-3 col-form-label">
                                    API-Key:<span style={{color: "red"}}>*</span>
                                </label>
                                <div className="col-sm-8">
                                    <input type="text"
                                           placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                                           id="apiKey"
                                           name="apiKey"
                                           className="form-control"
                                           onChange={e => setApiKey(e.target.value)}
                                           required
                                    />
                                </div>
                            </div>
                        )}

                        <button type="submit" className="btn mb-3"
                                style={{backgroundColor: '#3A1CF3', color: 'white'}}>
                            Erstellen
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );

}