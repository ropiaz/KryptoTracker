import React, {useState} from "react";
import axios from "axios";
import {useStateContext} from "../../contexts/ContextProvider.jsx";
import {useNavigate} from "react-router-dom";

const FileImportFormular = () => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [csvFile, setCsvFile] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files) {
            setCsvFile(e.target.files[0]);
        }
    };

    const handleFileUpload = async (ev) => {
        ev.preventDefault();
        if (!csvFile) {
            setErrors(["Bitte wählen Sie eine Datei aus."]);
            return;
        }

        const formData = new FormData();
        formData.append("csvFile", csvFile);

        try {
            const response = await axios.post(`${apiUrl}/file-import/`, formData, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Token ${token}`,
                }
            });
            console.log(response.data);

            setErrors([]);
            // navigate('/user/transactions');
            // window.location.reload();
        } catch (error) {
            console.error("Fehler beim Senden der Datei", error);
        }
    };

    return (
        <>
            {errors.length > 0 && (
                <div className="alert alert-danger">
                    {errors.map((error, index) => (
                        <div key={index}>{error}</div>
                    ))}
                </div>
            )}
            <form onSubmit={handleFileUpload} method="post">
                <div className="mb-3 col-md-6">
                    <label htmlFor="csvFile" className="form-label">Wähle die CSV-Datei aus</label>
                    <input type="file"
                           id="csvFile"
                           name="csvFile"
                           className="form-control form-control-sm"
                           onChange={handleFileChange}
                    />
                </div>

                <button type="submit" className="btn mb-3" style={{backgroundColor: '#3A1CF3', color: 'white'}}>
                    Einlesen
                </button>
            </form>
        </>
    );
}

// component to import the export csv file from crypto exchanges
// TODO: create formular to import transactions via csv data
export default function DataImport() {
    // const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    // const { token, setNotification } = useStateContext();
    // const navigate = useNavigate();
    // const [errors, setErrors] = useState([]);
    // const [csvFile, setCsvFile] = useState(null);
    //
    // const handleFileChange = (e) => {
    //     if (e.target.files) {
    //         setCsvFile(e.target.files[0]);
    //     }
    // };
    //
    // const handleFileUpload = async (ev) => {
    //     ev.preventDefault();
    //     if (!csvFile) {
    //         setErrors(["Bitte wählen Sie eine Datei aus."]);
    //         return;
    //     }
    //
    //     const formData = new FormData();
    //     formData.append("csvFile", csvFile);
    //
    //     try {
    //         const response = await axios.post(`${apiUrl}/file-import/`, formData, {
    //             xsrfCookieName: 'csrftoken',
    //             xsrfHeaderName: 'X-CSRFToken',
    //             headers: {
    //                 'Content-Type': 'multipart/form-data',
    //                 'Authorization': `Token ${token}`,
    //             }
    //         });
    //         console.log(response.data);
    //
    //         setErrors([]);
    //         // navigate('/user/transactions');
    //         // window.location.reload();
    //     } catch (error) {
    //         console.error("Fehler beim Senden der Datei", error);
    //     }
    // };

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Transaktionen mit CSV-Import</h2>
                    <div className="alert alert-warning alert-dismissible fade show" role="alert">
                        <strong>Achtung:</strong> Aktuell werden nur Exporte von Kraken akzeptiert! Bitte nur die <strong>ledgers.csv</strong> einlesen.
                        <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                    <FileImportFormular />
                </div>
            </div>
        </div>
    );
}