import React from "react";
import { useStateContext } from "../../contexts/ContextProvider";
import Stats from "./Stats";
import PortfolioAndStakingTables from "./BalanceTables";
import LastTransactions from "./LastTransactions";
import TaxReports from "./TaxReports";
import BalanceChart from "./BalanceChart";
import { getPortfolio } from "../../hooks/Portfolio.jsx";

export default function Dashboard(){
    const { token } = useStateContext();
    const { portfolioData, error, isLoading, isError } = getPortfolio();

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Benutzerdaten.</p>;
    }

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <h2>Dashboard</h2>

            <Stats portfolioData={portfolioData}/>
            <PortfolioAndStakingTables portfolioData={portfolioData} />
            <div className="row">
                <div className="col-md-6">
                    <BalanceChart />
                </div>
                <div className="col-md-6">
                    <LastTransactions portfolioData={portfolioData} />
                </div>
            </div>
            <div className="">
                <TaxReports />
            </div>
        </div>
    );
}
