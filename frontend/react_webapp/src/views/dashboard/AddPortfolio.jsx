import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { getPortfolioType } from "../../hooks/Portfolio.jsx";
import { useStateContext } from "../../contexts/ContextProvider.jsx";

const PorfolioFormular = ({ typeData }) => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [portfolio, setPortfolio] = useState({
        name: '',
        portfolioType: typeData[0].id || 1,
    });

    const handleChange = (e) => {setPortfolio({ ...portfolio, [e.target.name]: e.target.value }); };

    // TODO: validate fields
    const handleSubmit = async (ev) => {
        ev.preventDefault();

        let params = {
            name: portfolio.name,
            portfolio_type_id: parseInt(portfolio.portfolioType),
            balance: 0.0
        }

        try {
            await axios.post(`${apiUrl}/portfolio/`, params, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                }
            })
                .then((res) => {
                    setNotification('Portfolio erfolgreich erstellt! Weiterleitung...');
                    setErrors([]);
                    setPortfolio({});
                    navigate('/user/dashboard');
                })
                .catch((error) => {
                    if(error.response.status === 500) {
                        setErrors(["Serverfehler bitte später erneut versuchen."]);
                    }
                });
        } catch (err) {
            setErrors(["Fehler beim Erstellen des Portfolios."]);
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
                    <label htmlFor="comment" className="col-sm-3 col-form-label">
                        Portfolio-Name<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <input type="text"
                               className="form-control"
                               id="name"
                               name="name"
                               placeholder="Beispiel: Staking"
                               onChange={handleChange}
                               required
                        />
                    </div>
                </div>
                <div className="mb-3 row">
                    <label htmlFor="portfolioType" className="col-sm-3 col-form-label">
                        Portfolio-Typ auswählen<span style={{color: "red"}}>*</span>
                    </label>
                    <div className="col-sm-9">
                        <select id="portfolioType"
                                name="portfolioType"
                                className="form-select"
                                onChange={handleChange}
                                value={portfolio.portfolioType}
                                required
                        >
                            {typeData.map((pt, index) => (
                                <option key={index} value={pt.id}>{pt.type}</option>
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

// add portfolio component
export default function AddPortfolio() {
    const {portfolioTypeData, error, isLoading, isError} = getPortfolioType();
    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Transaktionsdaten.</p>;
    }

    const types = portfolioTypeData?.types;

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Portfolio hinzufügen</h2>

                    {types.length > 0 && (
                        <PorfolioFormular typeData={types} />
                    )}

                    {types.length === 0 && (
                        <p>Keine Typen zur Auswahl. Bitte später erneut versuchen.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
