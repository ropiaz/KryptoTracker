import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import { getTransactionTypes } from "../../hooks/Transaction.jsx";
import Select from 'react-select';
import { FixedSizeList as List } from 'react-window';

const MenuList = ({ options, children, maxHeight, getValue }) => {
    const height = 35;
    const value = getValue()[0]; // getValue gibt ein Array zurück, wir wollen das erste Element.
    let initialOffset = 0;

    if (value) {
        const index = options.findIndex(option => option.value === value.value);
        if (index >= 0) {
            initialOffset = index * height;
        }
    }

    // Wenn keine Kinder vorhanden sind (z.B. weil die Suche keine Treffer ergab), dann geben Sie eine entsprechende Nachricht zurück
    if (!children || !children.length) {
        return <div style={{ padding: '10px', textAlign: 'center' }}>Keine Treffer</div>;
    }

    return (
        <List
            height={maxHeight}
            itemCount={children.length}
            itemSize={height}
            initialScrollOffset={initialOffset}
        >
            {({ index, style }) => <div style={style}>{children[index]}</div>}
        </List>
    );
};

const TransactionFormular = ({ transType, portfolios, assetInfos}) => {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const { token, setNotification } = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [transaction, setTransaction] = useState({
        transactionType: transType[0].id || '',
        transactionDate: '',
        assetId: '',
        targetAssetId: '',
        amount: '',
        price: '',
        transactionFee: '',
        transactionHashId: '',
        senderAddress: '',
        recipientAddress: '',
        comment: '',
        portfolio: portfolios[0].id || ''
    });
    const [selectedAsset, setSelectedAsset] = useState(null);
    const [selectedTargetAsset, setSelectedTargetAsset] = useState(null);
    const [selectedTransactionType, setSelectedTransactionType] = useState(transaction.transactionType);

    const handleChange = (e) => {
        setTransaction({ ...transaction, [e.target.name]: e.target.value });

        // update selected transaction type
        if (e.target.name === 'transactionType') {
            setSelectedTransactionType(e.target.value);

            const isTrade = transType.find(tt => tt.id.toString() === e.target.value)?.type === "Handel";

            if (!isTrade) {
                // Wenn es nicht 'Handel' ist, leeren Sie die targetAssetId und das ausgewählte TargetAsset
                setTransaction(prev => ({ ...prev, targetAssetId: '' }));
                setSelectedTargetAsset(null);
            }
        }
    };

    // check if trade type is selected
    const isTradeTransaction = Number(selectedTransactionType) === transType.find(tt => tt.type === "Handel")?.id;

    // convert the asset information for use with react-select
    const assetOptions = assetInfos.map(asset => ({
        value: asset.id,
        label: `${asset.fullname} (${asset.acronym})`
    }));

    const handleAssetChange = selectedOption => {
        if (selectedOption) {
            // user select an option
            setSelectedAsset(selectedOption);
            setTransaction({ ...transaction, assetId: selectedOption.value });
        } else {
            // user delete selection
            setSelectedAsset(null);
            setTransaction({ ...transaction, assetId: '' });
        }
    };

    const handleTargetAssetChange = selectedOption => {
        if (selectedOption) {
            setSelectedTargetAsset(selectedOption);
            setTransaction({ ...transaction, targetAssetId: selectedOption.value });
        } else {
            setSelectedTargetAsset(null);
            setTransaction({ ...transaction, targetAssetId: '' });
        }
    };

    // TODO: error handling, validation
    const handleSubmit = async (ev) => {
        ev.preventDefault();

        console.log(transaction);

        const params = {
            transactionType: parseInt(transaction.transactionType),
            transactionDate: transaction.transactionDate,
            assetId: transaction.assetId,
            targetAssetId: parseInt(transaction.targetAssetId),
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
                    window.location.reload();
                })
                .catch((error) => {
                    setErrors([error.response.data.message])
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
                                    required
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
                                   required
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
                        <label htmlFor="asset" className="col-sm-3 col-form-label">
                            Kryptowährung<span style={{color: "red"}}>*</span>
                        </label>
                        <div className="col-sm-9">
                            <Select
                                components={{ MenuList }}
                                options={assetOptions}
                                onChange={handleAssetChange}
                                placeholder="Wählen oder Suchen Sie eine Kryptowährung: Bitcoin (btc) "
                                id="assetId"
                                name="assetId"
                                isClearable
                                isSearchable
                                required
                            />
                        </div>
                    </div>
                    {isTradeTransaction && (
                        <div className="mb-3 row">
                            <label htmlFor="asset" className="col-sm-3 col-form-label">
                                Ziel-Kryptowährung<span style={{color: "red"}}>*</span>
                            </label>
                            <div className="col-sm-9">
                                <Select
                                    components={{ MenuList }}
                                    options={assetOptions}
                                    onChange={handleTargetAssetChange}
                                    placeholder="Wählen oder Suchen Sie eine Kryptowährung: Ethereum (eth) "
                                    id="targetAssetId"
                                    name="targetAssetId"
                                    isClearable
                                    isSearchable
                                    required
                                />
                            </div>
                        </div>
                    )}
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
                                   required
                            />
                        </div>
                    </div>
                    <div className="mb-3 row">
                        <label htmlFor="price" className="col-sm-3 col-form-label">
                            Preis beim Handel
                        </label>
                        <div className="col-sm-9">
                            <input type="text"
                                   className="form-control"
                                   id="price"
                                   name="price"
                                   placeholder="Beispiel in EUR: 7758.20"
                                   onChange={handleChange}
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

// add transaction component
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
    const assetInfos = transactionTypeData?.asset_infos;

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Neue Transaktion hinzufügen</h2>
                    <TransactionFormular transType={types} portfolios={portfolios} assetInfos={assetInfos}/>
                </div>
            </div>
        </div>
    );
}
