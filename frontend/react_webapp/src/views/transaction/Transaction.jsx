import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { getTransactions } from "../../hooks/Transaction.jsx";

const List = ({ data }) => {
    return (
        <>
            <div className="table-responsive border-bottom border-black mb-3">
                <table className="table table-striped table-responsive table-sm">
                    <thead>
                    <tr>
                        <th scope="col"></th>
                        <th scope="col">Typ</th>
                        <th scope="col">Asset</th>
                        <th scope="col">Menge</th>
                        <th scope="col">Wert</th>
                        <th scope="col">Gebühr</th>
                        <th scope="col">Datum</th>
                        <th scope="col">Sender-Adresse</th>
                        <th scope="col">Empfänger-Adresse</th>
                        <th scope="col">Kommentar</th>
                        <th scope="col">Aktion</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td>
                                <input type="checkbox" autoComplete="off"/>
                            </td>
                            <td>{item.tx_type}</td>
                            <td>{item.asset}</td>
                            <td>{item.tx_amount}</td>
                            <td>{item.tx_value} €</td>
                            <td>{item.tx_fee} €</td>
                            <td>{item.tx_date}</td>
                            <td>{item.tx_sender_address}</td>
                            <td>{item.tx_recipient_address}</td>
                            <td>{item.tx_comment}</td>
                            <td>
                                <Link to="#" style={{textDecoration: 'none'}} className="me-2">Ändern</Link>
                                <Link to="#" style={{color: 'red', textDecoration: 'none'}}>Löschen</Link>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="d-flex flex-column flex-md-row justify-content-between align-items-center">
                <p>Einträge 1 bis {data.length} von {data.length}</p>
                <nav className="">
                    <ul className="pagination pagination-sm">
                        <li className="page-item"><a className="page-link" href="#">Zurück</a></li>
                        <li className="page-item"><a className="page-link active" href="#">1</a></li>
                        <li className="page-item"><a className="page-link" href="#">Nächste</a></li>
                    </ul>
                </nav>
            </div>
        </>
    );
}

// transaction history component that shows all transactions from users and can be edited
// TODO: search & filter function, pagination, create, edit, delete, data import
export default function Transaction(){
    // dummy data for transactions list
    // const data = [
    //     {tx_type: 'Staking', asset: 'BTC', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Handel', asset: 'ETH', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Staking', asset: 'ADA', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Kaufen', asset: 'ADA', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Verkaufen', asset: 'ETH', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Staking', asset: 'KAVA', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Staking', asset: 'XTZ', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    //     {tx_type: 'Handel', asset: 'DOT', tx_amount: 100.57, tx_value: 1000.54, tx_fee: 0.0, tx_date: '12.01.2023', tx_comment: 'Test Kommentar', tx_sender_address: 'sfASASFSADFDSAFas', tx_recipient_address: 'slsdkdnbasjhdg'},
    // ];
    const navigate = useNavigate();
    const { transactionData, error, isLoading, isError } = getTransactions();

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Transaktionsdaten.</p>;
    }

    const tx_data = transactionData?.transactions;

    const handleEditTransaction = () => {

    }

    const handleDeleteTransaction = () => {

    }

    const handleDataImport = () => {

    }

    const handleDataExport = () => {

    }


    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="col">
                <div className="card shadow-bg">
                    <div className="card-body">
                        <h2 className="mb-3">Transaktionshistorie</h2>
                        <div className="row">
                            <div className="col-12 col-md-auto mb-2">
                                <button className="btn btn-success btn-sm me-2" onClick={() => {navigate('/user/transactions/add')}}>Neu</button>
                                <button className="btn btn-secondary btn-sm me-2" onClick={handleEditTransaction} disabled>Edit</button>
                                <button className="btn btn-danger btn-sm me-2" onClick={handleDeleteTransaction} disabled >Löschen</button>
                                <button className="btn btn-warning btn-sm me-2" onClick={handleDataImport}>Datenimport</button>
                                <button className="btn btn-info btn-sm" onClick={handleDataExport}>CSV <i className="bi bi-download"></i></button>
                            </div>
                            <div className="col-12 col-md-auto ms-auto mb-3">
                                <div className="d-flex">
                                    <input type="text" className="form-control me-2" placeholder="Search"/>
                                    <select className="form-select" style={{width: 'auto'}}>
                                        <option value="10">10 Einträge</option>
                                        <option value="20">20 Einträge</option>
                                        <option value="50">50 Einträge</option>
                                        <option value="100">100 Einträge</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <List data={tx_data}/>
                    </div>
                </div>
            </div>
        </div>
    );
}
