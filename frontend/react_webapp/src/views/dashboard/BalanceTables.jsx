import React from 'react';

const BilanzTableComponent = ({ title, dataset }) => {
    const totalValue = dataset.reduce((acc, item) => acc + parseFloat(item.owned_value), 0).toFixed(2).replace('.', ',');

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
                        <img src={item.img} className="img-responsive" style={{ marginRight: '5px', height: '30px' }} alt="coin-img"/>
                        <span>{item.acronym}</span>
                      </td>
                      <td>{item.amount.toFixed(3).replace('.', ',')}</td>
                      <td>{item.price.toFixed(3).replace('.', ',')}</td>
                      <td>{item.owned_value.toFixed(3).replace('.', ',')}</td>
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

// dashboard component that shows owned assets in spot and staking portfolio
// TODO: Pagination max 10 on one page, Search in Datasets, Filter Columns
export default function PortfolioAndStakingTables({ portfolioData }){
    const spotData = portfolioData?.spot_data;
    const stakingData = portfolioData?.staking_data;
    return (
        <div className="row">
            {spotData.length > 0 && (
                <BilanzTableComponent dataset={spotData} title="Aktuelle Portfolio Bilanz" />
            )}
            {stakingData.length > 0 && (
                <BilanzTableComponent dataset={stakingData} title="Aktuelle Staking Bilanz" />
            )}
        </div>
    );
};