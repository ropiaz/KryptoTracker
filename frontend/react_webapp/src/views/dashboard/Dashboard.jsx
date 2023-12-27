import React from "react";
import { useStateContext } from "../../contexts/ContextProvider";
import { getUser } from "../../hooks/Auth";
import Stats from "./Stats";
import PortfolioAndStakingTables from "./BalanceTables";
import LastTransactions from "./LastTransactions";
import TaxReports from "./TaxReports";
import BalanceChart from "./BalanceChart";

export default function Dashboard(){
    const { token } = useStateContext();
    const { userData, isLoading, isError, error } = getUser(token);

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Benutzerdaten.</p>;
    }

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <h2>Dashboard</h2>
            {userData && <p>Angemeldet als: {userData.username}</p>}

            <Stats />
            <PortfolioAndStakingTables />
            <div className="row">
                <div className="col-md-6">
                    <BalanceChart />
                </div>
                <div className="col-md-6">
                    <LastTransactions />
                </div>
            </div>
            <div className="">
                <TaxReports />
            </div>
        </div>
    );
}
