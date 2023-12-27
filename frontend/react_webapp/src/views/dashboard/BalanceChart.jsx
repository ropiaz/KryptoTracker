import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// dummy data for chart
const data = [
  {name: 'BTC', value: 9000},
  {name: 'ETH', value: 3000},
  {name: 'LTC', value: 5000},
  {name: 'ADA', value: 8500},
  {name: 'EUR', value: 1000}
];

// <div className="d-flex justify-content-between align-items-center">
//   <h5 className="card-title">Bestand nach Währung</h5>
//   <div className="d-flex">
//     <select className="form-select form-select-sm mx-1" aria-label="FiatSelector">
//       <option defaultValue="EUR">EUR</option>
//       <option value="USD">USD</option>
//       {/* Weitere Optionen */}
//     </select>
//     <select className="form-select form-select-sm mx-1" aria-label="AssetSelector">
//       <option defaultValue="Alle Währungen">Alle Assets</option>
//       <option value="BTC">BTC</option>
//       <option value="ETH">ETH</option>
//       {/* Weitere Optionen */}
//     </select>
//   </div>
// </div>

// TODO: get Portfolio Data, display chart with select function fiat and coin
export default function BalanceChart() {
  return (
      <div className="card shadow-bg mb-3">
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <h5 className="card-title mb-3">Bestand nach Währung</h5>
            </div>
            <div className="col-md-3 mb-3">
              <select className="form-select" aria-label="FiatSelector">
                <option defaultValue="EUR">EUR</option>
                <option value="1">USD</option>
              </select>
            </div>
            <div className="col-md-3 mb-3">
              <select className="form-select" aria-label="AssetSelector">
                <option defaultValue="Alle Assets">Alle Assets</option>
                <option value="1">BTC</option>
                <option value="2">ETH</option>
                <option value="3">LTC</option>
                <option value="3">ADA</option>
                <option value="3">EUR</option>
              </select>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#3967AE" />
          </BarChart>
        </ResponsiveContainer>
        </div>
      </div>
  );
}
