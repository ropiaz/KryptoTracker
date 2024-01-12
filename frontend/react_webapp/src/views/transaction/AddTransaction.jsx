import React, { useState } from "react";
import 'axios';
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import { getTransactionTypes } from "../../hooks/Transaction.jsx";

const TransactionFormular = ({ transType, portfolios }) => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [transaction, setTransaction] = useState({
        transactionType: transType[0].id || '',
        transactionDate: '',
        assetName: '',
        assetAcronym: '',
        targetAssetName: '',
        targetAssetAcronym: '',
        amount: '',
        price: '',
        transactionFee: '',
        transactionHashId: '',
        senderAddress: '',
        recipientAddress: '',
        comment: '',
        portfolio: portfolios[0].id || ''
    });

    const handleChange = (e) => {
        setTransaction({ ...transaction, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (ev) => {
        ev.preventDefault();
        let newErrors = [];

        console.log(transaction);

        const params = {
            transactionType: transaction.transactionType,
            transactionDate: transaction.transactionDate,
            assetName: transaction.assetName,
            assetAcronym: transaction.assetAcronym,
            targetAssetName: transaction.targetAssetName,
            targetAssetAcronym: transaction.targetAssetAcronym,
            amount: parseFloat(transaction.amount),
            price: parseFloat(transaction.price),
            transactionFee: parseFloat(transaction.transactionFee),
            transactionHashId: transaction.transactionHashId,
            senderAddress: transaction.senderAddress,
            recipientAddress: transaction.recipientAddress,
            comment: transaction.comment,
            portfolio: transaction.portfolio
        }

        try {
            // const requiredFields = {
            //     transactionType: 'Transaktionstyp',
            //     transactionDate: 'Datum und Uhrzeit',
            //     asset: 'Kryptowährung',
            //     amount: 'Anzahl',
            //     price: 'Preis beim Handel',
            // };
            //
            // // Check for empty fields
            // for (const [key, value] of Object.entries(transaction)) {
            //     if(key === 'targetAsset'       ||
            //        key === 'transactionFee'    ||
            //        key === 'transactionHashId' ||
            //        key === 'senderAddress'     ||
            //        key === 'recipientAddress'  ||
            //        key === 'comment')
            //     {
            //         continue;
            //     }
            //     if (!value) {
            //         newErrors.push(`Das Feld ${requiredFields[key]} darf nicht leer sein.`);
            //     }
            // }
            //
            // if (newErrors.length > 0) {
            //     setErrors(newErrors);
            //     return;
            // }

            await axios.post(`${apiUrl}/transaction/`, params, {
                xsrfCookieName: 'csrftoken',
                xsrfHeaderName: 'X-CSRFToken',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                }
            })
                .then((res) => {
                    setNotification('Transaktion erfolgreich erstellt! Weiterleitung...');
                    setErrors([]);
                    navigate('/user/transactions');
                })
                .catch((error) => {
                    // TODO: display error messages from backend
                    console.log(error.data)
                    // setErrors([error.data.error])
                });
        } catch (err) {
            setErrors(["Fehler beim Erstellen der Transaktion."]);
        }
    };

    return (
        <>
            {errors.length > 0 && (
                    <div className="alert alert-danger">
                        {errors.map((error, index) => (
                            <div key={index}>{error}</div>
                        ))}
                    </div>
            )}
            <form onSubmit={handleSubmit} method="post">
                <fieldset>
                    <legend>Typ und Datum</legend>
                    <small><span style={{color: "red"}}>*</span>erforderlich</small>
                    <div className="mb-3 row">
                        <label htmlFor="transactionType" className="col-sm-3 col-form-label">
                            Transaktionstyp<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <select id="transactionType"
                                    name="transactionType"
                                    className="form-select"
                                    onChange={handleChange}
                                    value={transaction.transactionType}
                                // required
                            >
                                {transType.map((pt, index) => (
                                    <option key={index} value={pt.id}>{pt.type}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="transactionDate" className="col-sm-3 col-form-label">
                            Datum und Uhrzeit<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <input type="datetime-local"
                                   id="transactionDate"
                                   name="transactionDate"
                                   className="form-control"
                                   onChange={handleChange}
                                // required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="portfolio" className="col-sm-3 col-form-label">
                            Portfolio auswählen<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <select id="portfolio"
                                    name="portfolio"
                                    className="form-select"
                                    onChange={handleChange}
                                    value={transaction.portfolio}
                                    required
                            >
                                {portfolios.map((p, index) => (
                                    <option key={index} value={p.id}>{p.name} - {p.portfolio_type} </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </fieldset>

                <fieldset>
                    <legend>Transaktionsdaten</legend>
                    <small><span style={{color: "red"}}>*</span>erforderlich</small>
                    <div className="mb-3 row">
                        <label htmlFor="assetName" className="col-sm-3 col-form-label">
                            Kryptowährung (Name)<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="assetName"
                                   name="assetName"
                                   placeholder="Beispiel: Bitcoin"
                                   onChange={handleChange}
                                // required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="assetAcronym" className="col-sm-3 col-form-label">
                            Kryptowährung (Symbol)<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="assetAcronym"
                                   name="assetAcronym"
                                   placeholder="Beispiel: BTC"
                                   onChange={handleChange}
                                // required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="targetAssetName" className="col-sm-3 col-form-label">
                            Ziel-Kryptowährung (Name)
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="targetAssetName"
                                   name="targetAssetName"
                                   placeholder="Beispiel bei Handel: Ethereum"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="targetAssetAcronym" className="col-sm-3 col-form-label">
                            Ziel-Kryptowährung (Symbol)
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="targetAssetAcronym"
                                   name="targetAssetAcronym"
                                   placeholder="Beispiel bei Handel: ETH"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="amount" className="col-sm-3 col-form-label">
                            Anzahl<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="amount"
                                   name="amount"
                                   placeholder="Beispiel: 0.24"
                                   onChange={handleChange}
                                // required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="price" className="col-sm-3 col-form-label">
                            Preis beim Handel<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="price"
                                   name="price"
                                   placeholder="Beispiel in EUR: 7758.20"
                                   onChange={handleChange}
                                // required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="transactionFee" className="col-sm-3 col-form-label">
                            Transktionsgebühr
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="transactionFee"
                                   name="transactionFee"
                                   placeholder="Beispiel in EUR: 5.18"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="transactionHashId" className="col-sm-3 col-form-label">
                            Transaktions-ID
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="transactionHashId"
                                   name="transactionHashId"
                                   placeholder="Beispiel: 793cef3ebac9ca4000285afca6c3be0d33ad1a94874483"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="senderAddress" className="col-sm-3 col-form-label">
                            Sender-Adresse
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="senderAddress"
                                   name="senderAddress"
                                   placeholder="Beispiel: bc1qx8s20q6ztxsapcsvzkepxnnvmeget7p7utz987a2e63q"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="recipientAddress" className="col-sm-3 col-form-label">
                            Empfänger-Adresse
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="recipientAddress"
                                   name="recipientAddress"
                                   placeholder="Beispiel: bc1pc7jjkjt2pxxjuues7xfpldsq56het7pmmwtvquvl2qxr2zh"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="comment" className="col-sm-3 col-form-label">
                            Kommentar
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="comment"
                                   name="comment"
                                   placeholder="Beispiel: Aufbewahrung Kraken"
                                   onChange={handleChange}
                            />
                        </div>
                    </div>
                </fieldset>

                <div className="text-end">
                    <button type="submit" className="btn btn-success"
                            style={{backgroundColor: '#3A1CF3', color: 'white'}}>Hinzufügen
                    </button>
                </div>
            </form>
        </>
    );
}

// add asset component to portfolio
// TODO: create formular to add assets into portfolios
export default function AddTransaction() {
    const {transactionTypeData, isError, isLoading, error} = getTransactionTypes();

    if (isLoading) {
        return <p>Lädt...</p>;
    }

    if (isError) {
        return <p>Es gab einen Fehler beim Laden der Transaktionsdaten.</p>;
    }

    const types = transactionTypeData?.types;
    const portfolios = transactionTypeData?.portfolios;

    // const handleFileUpload = (ev) => {
    //     ev.preventDefault();
    //     // Hier würden Sie die CSV-Datei verarbeiten
    //     console.log(ev.target.files);
    // };

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    {/*<form onSubmit={handleFileUpload} method="post">*/}
                    {/*    <button type="submit" className="btn mb-3" style={{backgroundColor: '#3A1CF3', color: 'white'}}>*/}
                    {/*        CSV-Datenimport*/}
                    {/*        <input type="file" hidden/>*/}
                    {/*    </button>*/}
                    {/*</form>*/}
                    <h2>Neue Transaktion hinzufügen</h2>
                    <TransactionFormular transType={types} portfolios={portfolios}/>
                </div>
            </div>
        </div>
    );
}
