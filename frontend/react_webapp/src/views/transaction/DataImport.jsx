import React, { useState } from "react";
import axios from "axios";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import { useNavigate } from "react-router-dom";

const FileImportFormular = () => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(false);
    const [errors, setErrors] = useState([]);
    const [csvFile, setCsvFile] = useState(null);
    const [csvFile2, setCsvFile2] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setCsvFile(e.target.files[0]);
        }
    };

    const handleFileChange2 = (e) => {
        if (e.target.files) {
            setCsvFile2(e.target.files[0]);
        }
    };

    const handleFileUpload = async (ev) => {
        ev.preventDefault();
        if (!csvFile || !csvFile2) {
            setErrors(["Bitte wählen Sie die ledgers.csv und trades.csv Dateien aus."]);
            return;
        }

        setIsLoading(true);
        const formData = new FormData();
        formData.append("csvFile", csvFile);
        formData.append("csvFile2", csvFile2);

        try {
            const response = await axios.post(`${apiUrl}/file-import/`, formData, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Token ${token}`,
                }
            });

            if(response.status === 202){
                setErrors([response.data.message]);
            }

            if(response.status === 200){
                console.log(response.data);
                setErrors([]);
                setCsvFile(null);
                setCsvFile2(null);
                setNotification("Datenimport erfolgreich.");
                navigate('/user/dashboard');
                window.location.reload();
            }

        } catch (error) {
            setErrors([error.response.data.error]);
            console.error("Fehler beim Senden der Datei", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
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

                    <form onSubmit={handleFileUpload} method="post">
                        <div className="col-12 col-md-auto ms-auto mb-3">
                            <label htmlFor="exchange" className="form-label">Wähle eine Börse aus:</label>
                            <div className="d-flex">
                                <select name="exchange" className="form-select" style={{width: 'auto'}}>
                                    <option defaultValue="kraken">Kraken</option>
                                    <option value="binance" disabled>Binance</option>
                                    <option value="bitpanda" disabled>Bitpanda</option>
                                    <option value="coinbase" disabled>Coinbase</option>
                                </select>
                            </div>
                        </div>

                        <div className="mb-3 col-md-6">
                            <label htmlFor="csvFile" className="form-label">Wähle die trades.csv Datei aus:</label>
                            <input type="file"
                                   id="csvFile"
                                   name="csvFile"
                                   className="form-control form-control-sm"
                                   onChange={handleFileChange}
                            />
                        </div>

                        <div className="mb-3 col-md-6">
                            <label htmlFor="csvFile" className="form-label">Wähle die ledgers.csv Datei aus:</label>
                            <input type="file"
                                   id="csvFile2"
                                   name="csvFile2"
                                   className="form-control form-control-sm"
                                   onChange={handleFileChange2}
                            />
                        </div>

                        <button type="submit" className="btn mb-3" style={{backgroundColor: '#3A1CF3', color: 'white'}}>
                            Einlesen
                        </button>
                    </form>
                </>
                )}
        </>
    );
}

// component to import the export csv file from crypto exchanges
// TODO: create formular to import transactions via csv data
export default function DataImport() {
    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Transaktionen mit CSV-Import</h2>
                    <div className="alert alert-warning alert-dismissible fade show" role="alert">
                        <strong>Achtung:</strong> Aktuell werden nur Exporte von Kraken akzeptiert! Bitte nur die <strong>trades.csv</strong> und <strong>ledgers.csv</strong> einlesen.
                        <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                    <FileImportFormular />
                </div>
            </div>
        </div>
    );
}