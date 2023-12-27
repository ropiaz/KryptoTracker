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
    switch (transaction.type) {
        case 'Einzahlung': return receiveIcon;
        case 'Handel': return tradeIcon;
        case 'Staking-Reward': return earnIcon;
        case 'Gesendet': return sentIcon;
        default: return "https://placehold.jp/18/bdbdbd/ffffff/50x50.png?text=not+found";
    }
}

const TransactionItem = ({ transaction }) => (
    <div className="d-flex justify-content-between align-items-center mb-2">
        <div className="d-flex align-items-center">
            <img src={getIcon(transaction)} alt={transaction.type} style={{ marginRight: '10px', height: '45px' }} className="img-responsive" />
            <div>
                <div>{transaction.type}</div>
                <div>{transaction.date}</div>
            </div>
        </div>
        <div>
            <div>{transaction.amount}</div>
            <div>{transaction.value}</div>
        </div>
    </div>
);

// TODO: Get real Transactions Data
export default function LastTransactions(){
    const lastFiveTransactions = transactionsData.slice(-5);

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

