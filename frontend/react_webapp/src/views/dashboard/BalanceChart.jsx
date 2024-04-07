import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// custom tooltip component for displaying bar values
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const value = payload[0].value.toFixed(2).replace('.', ',');
    return (
      <div className="custom-tooltip">
        <span>{`${label} : ${value}`} €</span>
      </div>
    );
  }

  return null;
}

// interactive dashboard component that shows the user assets and their value in a bar chart with filter function
export default function BalanceChart({ dashboardData }) {
    const [selectedAssets, setSelectedAssets] = useState([]);
    const [filteredChartData, setFilteredChartData] = useState([]);

    // Optionen für den Select-Component, einschließlich der "Alle" Option
    const allOption = { value: 'All', label: 'Alle Assets' };
    const assetOptions = dashboardData?.chart_data.map(owned => ({
        value: owned.asset,
        label: owned.asset
    }));
    const options = [allOption, ...assetOptions];

    // initialize the selection with all assets if the portfolio data object is available
    useEffect(() => {
        if (dashboardData?.chart_data) {
          setSelectedAssets(assetOptions.map(option => option.value));
          setFilteredChartData(dashboardData.chart_data);
        }
    }, [dashboardData]);

    // update the filtered data when the selection changes
    useEffect(() => {
        if (dashboardData?.chart_data) {
            const filteredData = dashboardData.chart_data.filter(owned =>
                selectedAssets.includes(owned.asset)
            );
            setFilteredChartData(filteredData);
        }
    }, [selectedAssets, dashboardData]);

    const handleSelectChange = selectedOptions => {
        // check whether the "All" option is selected
        if (selectedOptions.some(option => option.value === allOption.value)) {
          // if all were already selected and "All" is selected again, cancel the selection
          if (selectedAssets.length === assetOptions.length) {
            setSelectedAssets([]);
          } else {
            // select all assets
            setSelectedAssets(assetOptions.map(option => option.value));
          }
        } else {
          // select the specific assets
          setSelectedAssets(selectedOptions.map(option => option.value));
        }
    };

    return (
        <div className="card shadow-bg mb-3">
          <div className="card-body">
              <div className="row">
                  <div className="col-md-6">
                      <h5 className="card-title mb-3">Bestand nach Währung</h5>
                  </div>
                  {dashboardData?.chart_data.length === 0 ? (
                      <p>Keine Daten verfügbar</p>
                  ) : (
                      <div className="col-md-6 mb-3">
                          <Select
                              options={options}
                              isMulti
                              closeMenuOnSelect={false}
                              onChange={handleSelectChange}
                              value={options.filter(option => selectedAssets.includes(option.value))}
                          />
                      </div>
                  )}
              </div>
              {dashboardData?.chart_data.length > 0 && (
                  <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={filteredChartData} margin={{top: 5, right: 30, left: 20, bottom: 25}}>
                          <CartesianGrid strokeDasharray="3 3"/>
                          <XAxis
                              dataKey="asset"
                              label={{
                                  value: 'Kryptowährungen',
                                  position: 'insideBottom',
                                  offset: -15,
                                  style: { textAnchor: 'middle' }
                              }}
                          />
                          <YAxis
                              label={{
                                  value: 'Euro',
                                  angle: -90,
                                  position: 'insideLeft',
                                  style: { textAnchor: 'middle' }
                              }}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend verticalAlign="top" wrapperStyle={{ lineHeight: '40px' }} />
                          <Bar dataKey="EUR" fill="#3967AE" />
                      </BarChart>
                  </ResponsiveContainer>
              )}
          </div>
        </div>
    );
}
