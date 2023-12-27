import React from 'react';

// dummy data for portfolio
const portfolioData = [
  { symbol: 'BTC', menge: '2,22', preis: '29132,03', wert: '64673,10', trend: '5.84%' },
  { symbol: 'ETH', menge: '304,88', preis: '1,543', wert: '470,42', trend: '4.90%' },
  { symbol: 'KAVA', menge: '304,88', preis: '0,743', wert: '470,42', trend: '1.90%' },
];

const stakingData = [
  { symbol: 'BTC', menge: '2,22', preis: '29132,03', wert: '64673,10', trend: '-5.84%' },
  { symbol: 'ETH', menge: '3004,88', preis: '1,543', wert: '4700,42', trend: '4.90%' },
  { symbol: 'XTZ', menge: '304,88', preis: '1,543', wert: '470,42', trend: '4.90%' },
  { symbol: 'DOT', menge: '304,88', preis: '1,543', wert: '470,42', trend: '4.90%' },
  { symbol: 'DEFI', menge: '304,88', preis: '1,543', wert: '470,42', trend: '4.90%' },
];

// TODO: Pagination, Get Portofolio Data, Search in Datasets
const BilanzTableComponent = ({ title, dataset }) => {
  const totalValue = dataset.reduce((acc, item) => acc + parseFloat(item.wert), 0).toFixed(2);

  return (
    <div className="col mb-3">
      <div className="card shadow-bg">
        <div className="card-body">
          <div className="row align-items-center mb-1">
            <div className="col-md-9">
              <h5 className="card-title">{title}</h5>
              <p className="card-text mb-3">Gesamtwert: {totalValue} €</p>
            </div>
            <div className="col-md-3">
              <input type="text" className="form-control" placeholder="Suche" />
            </div>
          </div>
          <div className="table-responsive border-bottom border-black mb-3">
            <table className="table table-striped table-sm">
            <thead className="border-black">
              <tr>
                <th scope="col">Währung</th>
                <th scope="col">Menge</th>
                <th scope="col">Preis der Währung</th>
                <th scope="col">Wert in EUR</th>
                <th scope="col">Trend</th>
              </tr>
            </thead>
            <tbody>
              {dataset.map((item, index) => (
                <tr key={index}>
                  <td>
                    <i className="bi bi-currency-exchange"></i> {item.symbol}
                  </td>
                  <td>{item.menge}</td>
                  <td>{item.preis}</td>
                  <td>{item.wert}</td>
                  <td className={item.trend.startsWith('-') ? 'text-danger' : 'text-success'}>
                    {item.trend}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-center">
            <p>Einträge 1 bis {dataset.length} von {dataset.length}</p>
            <nav className="">
              <ul className="pagination pagination-sm">
                <li className="page-item"><a className="page-link" href="#">Zurück</a></li>
                <li className="page-item"><a className="page-link active" href="#">1</a></li>
                <li className="page-item"><a className="page-link" href="#">Nächste</a></li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function PortfolioAndStakingTables(){
  return (
      <div className="row">
        <BilanzTableComponent dataset={portfolioData} title="Aktuelle Portfolio Bilanz" />
        <BilanzTableComponent dataset={stakingData} title="Aktuelle Staking Bilanz" />
      </div>
  );
};