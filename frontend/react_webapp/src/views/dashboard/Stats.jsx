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
export default function Stats({ dashboardData }) {
    const sumBalance = dashboardData?.sum_balance.toFixed(2).replace('.', ',');
    const spotBalance = dashboardData?.spot_balance.toFixed(2).replace('.', ',');
    const stakingBalance = dashboardData?.staking_balance.toFixed(2).replace('.', ',');
    const firstTransaction = dashboardData?.first_transaction;
    const lastTransaction = dashboardData?.last_transaction;
    const transactionsCount = dashboardData?.transactions.count;
    const transactionsWithCoins = dashboardData?.transactions.with_coins;

    const stats = [
        { title: 'Gesamtwert aller Währungen', value: sumBalance + ' €', additionalInfo: null },
        { title: 'Aktuelle Spot Bilanz', value: spotBalance + ' €', additionalInfo: null },
        { title: 'Aktuelle Staking Bilanz', value: stakingBalance + ' €', additionalInfo: null },
        { title: 'Erste Transaktion', value: firstTransaction, additionalInfo: null },
        { title: 'Letzte Transaktion', value: lastTransaction, additionalInfo: null },
        { title: 'Gesamtanzahl an Transaktionen', value: transactionsCount + ' Transaktionen', additionalInfo: `mit ${transactionsWithCoins} Coins` },
    ];

    return (
        <div className="row row-cols-1 row-cols-md-3 g-3 mb-3">
            {stats.length === 0
                ? <p>Keine Daten vorhanden</p>
                : stats.map((stat, index) => (
                    <StatCard
                        key={index}
                        title={stat.title}
                        value={stat.value}
                        additionalInfo={stat.additionalInfo}
                    />
                ))
            }

        </div>
    );
};

