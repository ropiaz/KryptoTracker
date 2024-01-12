import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import { getPortfolio } from "../../hooks/Portfolio.jsx";

// formular componenet
const AssetFormular = ({ portfolioData }) => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [asset, setAsset] = useState({
        quantityOwned: '',
        quantityPrice: '',
        acronym: '',
        name: '',
        portfolio: portfolioData[0].id || '',
    });

    const handleChange = (e) => { setAsset({...asset, [e.target.name]: e.target.value}); };

    // TODO: validate fields
    const handleSubmit = async (ev) => {
        ev.preventDefault();
        let newErrors = [];

        if(isNaN(asset.quantityOwned) || isNaN(asset.quantityPrice)) {
            newErrors.push('Bitte korrekte Zahlenwerte eingeben. (Punkt statt Komma)')
        }

        let params = {
            'quantity_owned': parseFloat(asset.quantityOwned),
            'quantity_price': parseFloat(asset.quantityPrice),
            'asset_acronym': asset.acronym,
            'asset_name': asset.name,
            'portfolio_id': parseInt(asset.portfolio),
        }

        if (newErrors.length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            await axios.post(`${apiUrl}/asset-owned/`, params, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                }
            })
                .then((res) => {
                    setNotification('Asset erfolgreich hinzugefügt! Weiterleitung...');
                    setErrors([]);
                    navigate('/user/dashboard');
                    window.location.reload();
                })
                .catch((error) => {
                    if(error.response.status === 500) {
                        setErrors(["Serverfehler bitte später erneut versuchen."]);
                    }
                });
        } catch (err) {
            setErrors(["Fehler beim Erstellen des Assets im Portfolio."]);
        }
    }

    return (
        <div>
            {errors.length > 0 && (
                <div className="alert alert-danger">
                    {errors.map((error, index) => (
                        <div key={index}>{error}</div>
                    ))}
                </div>
            )}
            <form onSubmit={handleSubmit} method="post">
                <small><span style={{color: "red"}}>*</span>erforderlich</small>
                <div className="mb-3 row">
                    <label htmlFor="name" className="col-sm-3 col-form-label">
                        Kryptowährung<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <input type="text"
                               className="form-control"
                               id="name"
                               name="name"
                               placeholder="Beispiel: Bitcoin"
                               onChange={handleChange}
                               required
                        />
                    </div>
                </div>
                <div className="mb-3 row">
                    <label htmlFor="acronym" className="col-sm-3 col-form-label">
                        Kryptowährung (kurz)<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <input type="text"
                               className="form-control"
                               id="acronym"
                               name="acronym"
                               placeholder="Beispiel: BTC"
                               onChange={handleChange}
                               required
                        />
                    </div>
                </div>
                <div className="mb-3 row">
                    <label htmlFor="quantityOwned" className="col-sm-3 col-form-label">
                        Menge in Besitz<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <input type="text"
                               className="form-control"
                               id="quantityOwned"
                               name="quantityOwned"
                               placeholder="Beispiel: 0.56"
                               onChange={handleChange}
                               required
                        />
                    </div>
                </div>
                <div className="mb-3 row">
                    <label htmlFor="quantityPrice" className="col-sm-3 col-form-label">
                        Aktueller Wert in €<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <input type="text"
                               className="form-control"
                               id="quantityPrice"
                               name="quantityPrice"
                               placeholder="Beispiel: 21133.30"
                               onChange={handleChange}
                               required
                        />
                    </div>
                </div>
                <div className="mb-3 row">
                    <label htmlFor="portfolio" className="col-sm-3 col-form-label">
                        Portfolio auswählen<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <select id="portfolio"
                                name="portfolio"
                                className="form-select"
                                onChange={handleChange}
                                value={asset.portfolio}
                                required
                        >
                            {portfolioData?.map((p, index) => (
                                <option key={index} value={p.id}>{p.name} - {p.type} </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="text-end">
                    <button type="submit" className="btn btn-success"
                            style={{backgroundColor: '#3A1CF3', color: 'white'}}>Hinzufügen
                    </button>
                </div>
            </form>
        </div>
    );
}

// component to add owned asset to portfolio
export default function AddAsset() {
    const {portfolioData, error, isLoading, isError} = getPortfolio();
    const portfolios = portfolioData?.portfolios;
    const navigate = useNavigate();

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Transaktionsdaten.</p>;
    }

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Asset erstellen und einem Portfolio hinzufügen</h2>

                    {portfolios.length > 0 && (
                        <AssetFormular portfolioData={portfolios}/>
                    )}
                    {portfolios.length === 0 && (
                        <>
                            <p>Benutzer hat keine Portfolios.</p>
                            <p>Bitte zuerst ein Portfolio erstellen:</p>
                            <button type="button"
                                    className="btn btn-success"
                                    onClick={(ev) => {navigate('/user/add-portfolio')}}
                            >
                                Portfolio erstellen
                            </button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
