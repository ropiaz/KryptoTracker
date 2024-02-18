import React, { useState } from 'react';

const BilanzTableComponent = ({ title, dataset }) => {
    const [showNullValues, setShowNullValues] = useState(false);
    const totalValue = dataset.reduce((acc, item) => acc + parseFloat(item.owned_value), 0).toFixed(3).replace('.', ',');
    const filteredDataset = showNullValues ? dataset.filter(item => parseFloat(item.amount) > 0.00099 && parseFloat(item.owned_value) !== 0.000) : dataset;
    const lenDataset = filteredDataset.length;

    return (
        <div className="col mb-3">
          <div className="card shadow-bg">
              <div className="card-body">
                  <div className="row align-items-center mb-1">
                      <div className="col-md-8">
                          <h5 className="card-title">{title}</h5>
                          <p className="card-text mb-3">Gesamtwert: {totalValue} €</p>
                          <span className="d-flex card-text mb-2">
                              <input type="checkbox"
                                     id="showNull"
                                     name="showNull"
                                     className="me-2"
                                     onChange={() => setShowNullValues(!showNullValues)}
                              />
                            Kleine Beträge (&lt; 0,00099) ausblenden
                          </span>
                      </div>
                      <div className="col-md-4">
                          <input type="text" className="form-control" placeholder="Suche"/>
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
                          {filteredDataset.map((item, index) => (
                              <tr key={index}>
                                  <td>
                                      <img src={item.img} className="img-responsive"
                                           style={{marginRight: '5px', height: '25px'}} alt="coin"/>
                                      <span>{item.acronym}</span>
                                  </td>
                                  <td className={parseFloat(item.amount) < 0.0 ? 'text-danger' : ''}>{item.amount.toFixed(3).replace('.', ',')}</td>
                                  <td>{item.price.toFixed(3).replace('.', ',')}</td>
                                  <td className={parseFloat(item.owned_value) < 0.0 ? 'text-danger' : ''}>{item.owned_value.toFixed(3).replace('.', ',')}</td>
                                  <td className={item.trend.startsWith('-') ? 'text-danger' : 'text-success'}>
                                      {item.trend}
                                  </td>
                              </tr>
                          ))
                          }
                          </tbody>
                      </table>
                  </div>
                  <div className="d-flex flex-column flex-md-row justify-content-between align-items-center">
                      {lenDataset > 0
                          ? (
                              <>
                                  <p>Einträge 1 bis {filteredDataset.length} von {filteredDataset.length}</p>
                                  <nav>
                                      <ul className="pagination pagination-sm">
                                          <li className="page-item"><a className="page-link" href="#">Zurück</a></li>
                                          <li className="page-item"><a className="page-link active" href="#">1</a></li>
                                          <li className="page-item"><a className="page-link" href="#">Nächste</a></li>
                                      </ul>
                                  </nav>
                              </>
                          )
                          : <p>Keine Einträge</p>
                      }
                  </div>
              </div>
          </div>
        </div>
    );
};

// dashboard component that shows owned assets in spot and staking portfolio
// TODO: Pagination max 10 on one page, Search in Datasets, Filter Columns
export default function PortfolioAndStakingTables({dashboardData}) {
    const portfoliosData = dashboardData?.portfolios_data;
    return (
        <div className="row">
            {portfoliosData.length > 0 && (
                portfoliosData.map((pData, index) => (
                    <BilanzTableComponent key={index} dataset={pData.currencies} title={pData.name + " - " + pData.type} />
                ))
            )}
        </div>
    );
};