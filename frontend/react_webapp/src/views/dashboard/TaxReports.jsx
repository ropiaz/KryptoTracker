import React from "react";

// dummy data for tax reports component
const tax_data = [
    {year: 2022, created_at: '01/02/2023', earn: 444.20},
    {year: 2021, created_at: '03/02/2022', earn: 592.20},
    {year: 2020, created_at: '06/02/2021', earn: -250.20},
    {year: 2019, created_at: '13/02/2020', earn: 754.20},
    {year: 2018, created_at: '13/02/2019', earn: 754.20},
    {year: 2017, created_at: '13/02/2018', earn: 754.20}
];

export default function TaxReports() {
    const sortedTaxData = [...tax_data]
        .sort((a, b) => b.year - a.year)
        .slice(0, 5);

    const formatCurrency = (value) => {
        const currency = value < 0 ? `Verlust -${Math.abs(value).toFixed(2)} €` : `Gewinn ${value.toFixed(2)} €`;
        const currencyClass = value < 0 ? 'text-danger' : 'text-success';
        return <span className={currencyClass}>{currency}</span>;
    };

    return (
        <div className="col-md-6">
            <div className="card shadow-bg">
                <div className="card-body">
                    <h5 className="card-title mb-3">Steuerberichte</h5>
                    {sortedTaxData.map((tax, index) => (
                        <div key={index} className="card m-2">
                            <div className="card-body border-bottom">
                                <div className="row align-items-center">
                                    <div className="col">
                                        <strong>{tax.year}</strong>
                                        <div>Erstellt am {tax.created_at}</div>
                                    </div>
                                    <div className="col-auto">
                                        {formatCurrency(tax.earn)}
                                    </div>
                                    <div className="col-auto">
                                        <button className="btn btn-primary" style={{backgroundColor: "#112738", border: "none"}}>Download</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                    <div className="mt-3">
                        <a href="#" className="card-link">Zeige alle Steuerberichte</a>
                    </div>
                </div>
            </div>
        </div>
    );
}