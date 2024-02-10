import React from 'react';
import { Link } from "react-router-dom";
import earnIcon from '../../assets/earn-stake.png';
import receiveIcon from '../../assets/receive.png';
import sentIcon from '../../assets/sent.png';
import tradeIcon from '../../assets/trade.png';

// Return icon img-path according to transaction type id
const getIcon = (transaction) => {
    switch (transaction.tx_type) {
        case "Reward": return earnIcon;
        case "Kaufen": return receiveIcon;
        case "Verkaufen": return sentIcon;
        case "Handel": return tradeIcon;
        case "Transfer": return tradeIcon;
        case "Gesendet": return sentIcon;
        case "Einzahlung": return earnIcon;
        case "Auszahlung": return sentIcon;
        default: return "https://placehold.jp/18/bdbdbd/ffffff/50x50.png?text=not+found";
    }
}

// dashboard component that shows the last five transactions
const TransactionItem = ({ transaction }) => (
    <div className="d-flex justify-content-between align-items-center mb-2">
        <div className="d-flex align-items-center">
            <img src={getIcon(transaction)} alt={transaction.tx_type} style={{ marginRight: '10px', height: '45px' }} className="img-responsive" />
            <div>
                <div>{transaction.tx_type}</div>
                <div>{transaction.tx_date}</div>
            </div>
        </div>
        <div>
            <div className="text-end">{transaction.tx_amount.toFixed(3).replace('.', ',')} {transaction.asset}</div>
            <div className="text-end">{transaction.tx_value.toFixed(3).replace('.', ',')} €</div>
        </div>
    </div>
);

// dashboard component that shows the last five transactions
export default function LastTransactions({ dashboardData }){
    const lastFiveTransactions = dashboardData?.last_five_transactions;
    return (
        <div className="mb-3">
            <div className="card shadow-bg">
                <div className="card-body">
                    <h5 className="card-title mb-3">Letzte Transaktionen</h5>
                    {lastFiveTransactions.length === 0 && (
                        <p>Keine Daten verfügbar</p>
                    )}
                    {lastFiveTransactions.length > 0 && lastFiveTransactions.map((transaction, index) => (
                        <TransactionItem key={index} transaction={transaction} />
                    ))}
                    {lastFiveTransactions.length > 0 && (
                        <div className="mt-3">
                            <Link to="/user/transactions" className="card-link">Zeige alle Transaktionen</Link>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

