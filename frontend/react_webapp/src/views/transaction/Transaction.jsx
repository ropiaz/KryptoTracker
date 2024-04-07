import React, { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { getTransactions } from "../../hooks/Transaction.jsx";
import { useStateContext } from "../../contexts/ContextProvider.jsx";

const List = ({ data, onDelete }) => {
    const navigate = useNavigate();
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
                        <th scope="col">Transaktions-ID</th>
                        {/*<th scope="col">Sender-Adresse</th>*/}
                        {/*<th scope="col">Empfänger-Adresse</th>*/}
                        <th scope="col">Kommentar</th>
                        <th scope="col">Systemstatus</th>
                        <th scope="col">Aktion</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.length === 0 && (
                        <tr>
                            <td colspan="11" className="py-3 text-center">
                                <span>
                                    Sie haben noch keine Transaktionen. Klicke Sie auf <strong>Neu</strong>, um Ihren ersten Handel hinzuzufügen
                                    oder wählen Sie <strong>Datenimport</strong> aus, um ihre Transaktionen zu importieren.
                                </span>
                            </td>
                        </tr>
                    )}
                    {data.length > 0 && (
                        data.map((item, index) => (
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
                                <td>{item.tx_hash}</td>
                                {/*<td>{item.tx_sender_address}</td>*/}
                                {/*<td>{item.tx_recipient_address}</td>*/}
                                <td>{item.tx_comment}</td>
                                <td>{item.tx_status}</td>
                                <td>
                                    <Link to="#"
                                          style={{textDecoration: 'none'}}
                                          className="me-2"
                                          onClick={() => navigate(`/user/transactions/edit/${item.tx_id}`)}
                                    >
                                        Ändern
                                    </Link>
                                    <Link to="#"
                                          style={{color: 'red', textDecoration: 'none'}}
                                          onClick={() => onDelete(item.tx_id)}
                                    >
                                        Löschen
                                    </Link>
                                </td>
                            </tr>
                        ))
                    )}
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

const ConfirmationModal = ({ show, onClose, onConfirm, message }) => {
    return (
        <div className={`modal ${show ? "show" : ""}`} style={{ display: show ? "block" : "none" }}>
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Bestätigung</h5>
                        <button type="button" className="btn-close" onClick={onClose}></button>
                    </div>
                    <div className="modal-body">
                        <p>{message}</p>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>Abbrechen</button>
                        <button type="button" className="btn btn-danger" onClick={onConfirm}>Löschen</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// transaction history component that shows all transactions from users and can be edited
// TODO: search & filter function, pagination, edit, data import
export default function Transaction() {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const navigate = useNavigate();
    const { token, setNotification } = useStateContext();
    const { transactionData, error, isLoading, isError } = getTransactions();
    const [showModal, setShowModal] = useState(false);
    const [selectedTxId, setSelectedTxId] = useState(null);

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Transaktionsdaten.</p>;
    }

    const tx_data = transactionData?.transactions;

     const openModal = (txId) => {
        setSelectedTxId(txId);
        setShowModal(true);
    };

    const closeModal = () => {
        setShowModal(false);
    };

    const confirmDelete = () => {
        handleDeleteTransaction(selectedTxId);
        closeModal();
    };

    const handleEditTransaction = () => {

    }

    const handleDeleteTransaction = async (txId) => {
        try {
            const response = await axios.delete(`${apiUrl}/transaction/${txId}`, {
                headers: {
                    Authorization: `Token ${token}`
                }
            });
            if (response.status === 204) {
                setNotification("Transaktion erfolgreich gelöscht.");
                navigate('/user/transactions');
                window.location.reload();
            }
        } catch (error) {
            setNotification("Fehler beim Löschen der Transaktion.");
            console.error("Fehler beim Löschen der Transaktion", error);
        }
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
                                <button className="btn btn-success btn-sm me-2" onClick={() => {
                                    navigate('/user/transactions/add')
                                }}>Neu
                                </button>
                                <button className="btn btn-secondary btn-sm me-2" onClick={handleEditTransaction}
                                        disabled>Edit
                                </button>
                                <button className="btn btn-danger btn-sm me-2" onClick={handleDeleteTransaction}
                                        disabled>Löschen
                                </button>
                                <button className="btn btn-warning btn-sm me-2" onClick={() => {
                                    navigate('/user/transactions/import')
                                }}>Datenimport
                                </button>
                                <button className="btn btn-info btn-sm" onClick={handleDataExport}>CSV <i
                                    className="bi bi-download"></i></button>
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
                        <List data={tx_data} onDelete={openModal}/>
                        <ConfirmationModal
                            show={showModal}
                            onClose={closeModal}
                            onConfirm={confirmDelete}
                            message="Sind Sie sicher, dass Sie diese Transaktion löschen möchten?"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
