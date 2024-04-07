import React from "react";
import Stats from "./Stats";
import PortfolioAndStakingTables from "./BalanceTables";
import LastTransactions from "./LastTransactions";
import TaxReports from "./TaxReports";
import BalanceChart from "./BalanceChart";
import { getDashboard } from "../../hooks/Portfolio.jsx";

export default function Dashboard(){
    const { dashboardData, error, isLoading, isError } = getDashboard();

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Benutzerdaten.</p>;
    }

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <h2>Dashboard</h2>

            <Stats dashboardData={dashboardData}/>
            <PortfolioAndStakingTables dashboardData={dashboardData} />
            <div className="row">
                <div className="col-md-6">
                    <BalanceChart dashboardData={dashboardData}/>
                </div>
                <div className="col-md-6">
                    <LastTransactions dashboardData={dashboardData} />
                </div>
            </div>
            <div className="">
                <TaxReports />
            </div>
        </div>
    );
}
