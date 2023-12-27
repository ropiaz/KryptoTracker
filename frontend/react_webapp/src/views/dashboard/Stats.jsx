import React from "react";

// single card component for statistics
const StatCard = ({ title, value, additionalInfo }) => (
    <div className="col">
        <div className="card h-100 shadow-bg">
              <div className="card-body">
                  <h5 className="card-title">{title}</h5>
                  <p className="card-text">{value}</p>
                  {additionalInfo && <p className="card-text"><small className="text-muted">{additionalInfo}</small></p>}
              </div>
        </div>
    </div>
);

// dashboard statistics component that includes all cards
// TODO: GET Portfolio Data from DB
export default function Stats() {
    // dummy data for statistic cards
    const stats = [
        { title: 'Gesamtwert aller Währungen', value: '70292,58 €', additionalInfo: null },
        { title: 'Aktuelle Portfolio Bilanz', value: '65162,85 €', additionalInfo: null },
        { title: 'Aktuelle Staking Bilanz', value: '5129,73 €', additionalInfo: null },
        { title: 'Erste Transaktion', value: '08.09.2018', additionalInfo: null },
        { title: 'Letzte Transaktion', value: '23.10.2023', additionalInfo: null },
        { title: 'Gesamtanzahl an Transaktionen', value: '6 Transaktionen', additionalInfo: 'mit 2 Coins' },
    ];

    return (
        <div className="row row-cols-1 row-cols-md-3 g-3 mb-3">
            {stats.map((stat, index) => (
                <StatCard
                    key={index}
                    title={stat.title}
                    value={stat.value}
                    additionalInfo={stat.additionalInfo}
                />
            ))}
        </div>
    );
};

