import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import axios from "axios";

export default function Tax(){
    const navigate = useNavigate();
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const [errors, setErrors] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showDatePeriod, setShowDatePeriod] = useState(false);
    const [taxInfo, setTaxInfo] = useState({
        'taxYear': null,
        'fromDate': null,
        'toDate': null,
    });

    const handleChange = (e) => {
        if(!showDatePeriod){
            setTaxInfo({ ...taxInfo, 'taxYear': e.target.value, 'fromDate': null, 'toDate': null });
        } else {
            setTaxInfo({ ...taxInfo, 'taxYear': null, [e.target.id]: e.target.value });
        }
    };

    const handleCreateTaxReport = async (ev) => {
        ev.preventDefault();

        try {
            if(showDatePeriod && (taxInfo.fromDate > taxInfo.toDate)){
                setErrors(["Das 'Von' Datum darf nicht nach dem 'Bis' Datum liegen."]);
                return;
            }

            const response = await axios.post(`${apiUrl}/tax-report/`, taxInfo, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                },
                responseType: "blob"
            });

            setIsLoading(true);

            if(response.status === 204){
                setErrors(["Zu diesem Steuerjahr wurden keine Transaktionen gefunden."]);
            }

            if(response.status === 201) {
                const data = taxInfo.taxYear != null ? taxInfo.taxYear : `${taxInfo.fromDate}-${taxInfo.toDate}`
                const filename = `kryptotracker-tax-report_${data}.pdf`

                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', filename); // Setzt den Dateinamen für den Download
                document.body.appendChild(link);
                link.click(); // Simuliert den Klick auf den Download-Link
                document.body.removeChild(link); // Entfernt den temporären Link
                window.URL.revokeObjectURL(url); // Bereinigt die Blob-URL

                setNotification("Steuerbericht erstellt.");
                setErrors([]);
                navigate('/user/dashboard');
                window.location.reload();
            }

        } catch (error) {
            setErrors([error.response.data.message]);
            console.error("Fehler beim Senden der Datei", error);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Erstellung eines Steuerberichts</h2>

                    <div className="mb-3">
                        <p className="card-text">
                            Der Steuerbericht kann für ein Steuerjahr oder einen wählbaren Zeitraum erstellt werden.<br/>
                            Das Steuerjahr ist standardgemäß aktiviert. Wenn ein wählbarer Zeitraum gewünscht ist, bitte mit dem Kontrollkästchen bestätigen.
                        </p>
                        <span className="d-flex card-text mb-2">
                              <input type="checkbox"
                                     id="showNull"
                                     name="showNull"
                                     className="me-2"
                                     onChange={() => setShowDatePeriod(!showDatePeriod)}
                              />
                            Zeitraum angeben
                          </span>
                    </div>

                    {isLoading ? (
                        <div className="d-flex justify-content-center align-items-center">
                            <div className="spinner me-2"></div>
                            <span>Lädt... Daten werden verarbeitet, bitte um Geduld.</span>
                        </div>
                    ) : (
                        <>
                            {errors.length > 0 && (
                                <div className="alert alert-danger">
                                    {errors.map((error, index) => (
                                        <div key={index}>{error}</div>
                                    ))}
                                </div>
                            )}

                            <form onSubmit={handleCreateTaxReport} method="get">

                                {!showDatePeriod ? (
                                    <div className="mb-3 row">
                                        <label htmlFor="taxYear" className="col-sm-3 col-form-label">
                                            Wähle das Steuerjahr aus:<span style={{color: "red"}}>*</span>
                                        </label>
                                        <div className="col-sm-8">
                                            <input type="number"
                                                   min="2011" max="2099" step="1"
                                                   placeholder="Beispiel: 2023"
                                                   id="taxYear"
                                                   name="taxYear"
                                                   className="form-control"
                                                   onChange={handleChange}
                                                   required
                                            />
                                        </div>
                                    </div>
                                ) : (
                                    <div className="mb-3 row">
                                        <label htmlFor="fromUntilDate" className="col-sm-3 col-form-label">
                                            Wähle den Zeitraum aus:<span style={{color: "red"}}>*</span>
                                        </label>
                                        <div className="col-sm-4">
                                            <span>von:</span>
                                            <input type="date"
                                                   id="fromDate"
                                                   name="fromDate"
                                                   className="form-control"
                                                   onChange={handleChange}
                                                   required
                                            />
                                        </div>
                                        <div className="col-sm-4">
                                            <span>bis</span>
                                            <input type="date"
                                                   id="toDate"
                                                   name="toDate"
                                                   className="form-control"
                                                   onChange={handleChange}
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
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
