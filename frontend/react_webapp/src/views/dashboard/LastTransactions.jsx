import React from 'react';
import earnIcon from '../../assets/earn-stake.png';
import receiveIcon from '../../assets/receive.png';
import sentIcon from '../../assets/sent.png';
import tradeIcon from '../../assets/trade.png';

// dummy data for last transactions
const transactionsData = [
    { type: 'Gesendet', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Gesendet', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Gesendet', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Gesendet', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Einzahlung', date: '01/11/23', amount: '+0.0190 BTC', value: '45,00 EUR' },
    { type: 'Gesendet', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Einzahlung', date: '01/11/23', amount: '+0.0190 BTC', value: '45,00 EUR' },
    { type: 'Handel', date: '01/11/23', amount: '+0.0190 BTC', value: '45,00 EUR' },
    { type: 'Staking-Reward', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
    { type: 'Staking-Reward', date: '01/11/23', amount: '+0.0190 ETH', value: '45,00 EUR' },
];

const getIcon = (transaction) => {
    switch (transaction.tx_type) {
        case 1: return earnIcon;
        case 2: return receiveIcon;
        case 3: return sentIcon;
        case 4: return tradeIcon;
        default: return "https://placehold.jp/18/bdbdbd/ffffff/50x50.png?text=not+found";
    }
}

const getType = (transaction) => {
    switch (transaction.tx_type) {
        case 1: return "Staking-Reward";
        case 2: return "Einzahlung";
        case 3: return "Gesendet";
        case 4: return "Handel";
        default: return "Undefiniert";
    }
}

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

// TODO: Get real Transactions Data
export default function LastTransactions({ portfolioData }){
    const lastFiveTransactions = portfolioData?.last_five_transactions;

    return (
        <div className="mb-3">
            <div className="card shadow-bg">
                <div className="card-body">
                    <h5 className="card-title mb-3">Letzte Transaktionen</h5>
                        {lastFiveTransactions.map((transaction, index) => (
                            <TransactionItem key={index} transaction={transaction} />
                        ))}
                    <div className="mt-3">
                        <a href="#" className="card-link">Zeige alle Transaktionen</a>
                    </div>
               </div>
            </div>
        </div>
    );
};

