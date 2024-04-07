import React from "react";
import axios from "axios";
import { useStateContext } from "../../contexts/ContextProvider.jsx";

export default function TaxReports({dashboardData}) {
    const { token, setNotification } = useStateContext();
    const taxData = dashboardData?.tax_data;
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const formatCurrency = (value) => {
        const currency = value < 0 ? `Verlust -${Math.abs(value).toFixed(2)} €` : `Gewinn ${value.toFixed(2)} €`;
        const currencyClass = value < 0 ? 'text-danger' : 'text-success';
        return <span className={currencyClass}>{currency}</span>;
    };

    const handleDownload = async (id) => {
        try {
            const response = await axios.get(`${apiUrl}/tax-report/${id}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
                responseType: 'blob'
            });

            if (response.status === 200){
                const filename = `kryptotracker-tax-report.pdf`;
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', filename); // Setzt den Dateinamen für den Download
                document.body.appendChild(link);
                link.click(); // Simuliert den Klick auf den Download-Link
                document.body.removeChild(link); // Entfernt den temporären Link
                window.URL.revokeObjectURL(url); // Bereinigt die Blob-URL
                setNotification("Steuerbericht heruntergeladen.");
            }
        } catch (error) {
            console.error('Download fehlgeschlagen', error);
            setNotification("Fehler beim Herunterladen des Steuerberichts.");
        }
    }

    return (
        <div className="col-md-6">
            <div className="card shadow-bg">
                <div className="card-body">
                    <h5 className="card-title mb-3">Steuerberichte</h5>
                    {taxData.length === 0 && (
                        <p>Keine Daten verfügbar</p>
                    )}
                    {taxData.length > 0 && (
                        taxData.map((tax, index) => (
                        <div key={index} className="card m-2">
                            <div className="card-body border-bottom">
                                <div className="row align-items-center">
                                    <div className="col">
                                        <strong>{tax.time_period}</strong>
                                        <div>Erstellt am {tax.created_at}</div>
                                    </div>
                                    <div className="col-auto">
                                        {formatCurrency(tax.income_trading + tax.income_staking)}
                                    </div>
                                    <div className="col-auto">
                                        <button className="btn btn-primary"
                                                style={{backgroundColor: "#112738", border: "none"}}
                                                onClick={() => {handleDownload(tax.id)}}
                                        >
                                            Download
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        ))
                    )}
                    {taxData.length > 0 && (
                        <div className="mt-3">
                            <a href="#" className="card-link">Zeige alle Steuerberichte</a>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}