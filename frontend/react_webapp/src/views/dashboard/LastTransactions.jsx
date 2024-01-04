import React from 'react';
import earnIcon from '../../assets/earn-stake.png';
import receiveIcon from '../../assets/receive.png';
import sentIcon from '../../assets/sent.png';
import tradeIcon from '../../assets/trade.png';
import { Link } from "react-router-dom";

// Return icon img-path according to transaction type id
const getIcon = (transaction) => {
    switch (transaction.tx_type) {
        case 1: return earnIcon;
        case 2: return receiveIcon;
        case 3: return sentIcon;
        case 4: return tradeIcon;
        default: return "https://placehold.jp/18/bdbdbd/ffffff/50x50.png?text=not+found";
    }
}

// Return transaction type in text according to transaction type id
const getType = (transaction) => {
    switch (transaction.tx_type) {
        case 1: return "Staking-Reward";
        case 2: return "Einzahlung";
        case 3: return "Gesendet";
        case 4: return "Handel";
        default: return "Undefiniert";
    }
}

// dashboard component that shows the last five transactions
const TransactionItem = ({ transaction }) => (
    <div className="d-flex justify-content-between align-items-center mb-2">
        <div className="d-flex align-items-center">
            <img src={getIcon(transaction)} alt={transaction.tx_type} style={{ marginRight: '10px', height: '45px' }} className="img-responsive" />
            <div>
                <div>{getType(transaction)}</div>
                <div>{transaction.tx_date}</div>
            </div>
        </div>
        <div>
            <div>{transaction.tx_amount.toFixed(3).replace('.', ',')} {transaction.asset}</div>
            <div>{transaction.tx_value.toFixed(3).replace('.', ',')} €</div>
        </div>
    </div>
);

// dashboard component that shows the last five transactions
export default function LastTransactions({ portfolioData }){
    const lastFiveTransactions = portfolioData?.last_five_transactions;

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

