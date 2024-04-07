import React, { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import { useStateContext } from "../../contexts/ContextProvider.jsx";
import axios from "axios";

const ListApiTable = ({data}) => {

    const formatSecret = (secret) => {
      if (secret.length > 7) {
        const start = secret.substring(0, 5);
        const end = secret.substring(secret.length - 2);
        return `${start}**********${end}`;
      }
      return secret;
    }

    return (
        <>
            <div className="table-responsive border-bottom border-black mb-3">
                <table className="table table-striped table-responsive table-sm">
                    <thead>
                    <tr>
                        <th scope="col"></th>
                        <th scope="col">Börse</th>
                        <th scope="col">API-Key</th>
                        <th scope="col">API-Sec</th>
                        <th scope="col mx-1">Aktion</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.length === 0 && (
                        <tr>
                            <td colSpan="5" className="py-3 text-center">
                                <span>
                                    Sie haben noch keine API-Schlüssel integriert. Klicke Sie auf <strong>API hinzufügen</strong>, um ihre Börse zu verbinden.
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
                                <td>{item.exchange_name}</td>
                                <td>{formatSecret(item.api_key)}</td>
                                <td>{formatSecret(item.api_sec)}</td>
                                <td>
                                    <Link to="#"
                                          style={{textDecoration: 'none'}}
                                          className="me-2"
                                          // onClick={() => navigate(`/user/transactions/edit/${item.tx_id}`)}
                                    >
                                        Ändern
                                    </Link>
                                    <Link to="#"
                                          style={{color: 'red', textDecoration: 'none'}}
                                          // onClick={() => onDelete(item.tx_id)}
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
                <p>Einträge {data.length} von {data.length}</p>
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

export default function ShowApi() {
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;
    const {token, setNotification} = useStateContext();
    const navigate = useNavigate();
    const [errors, setErrors] = useState([]);
    const [apiData, setApiData] = useState({
        'apiKey': null,
        'apiSec': null,
        'exchangeName': null,
    });

    const [apiData2, setApiData2] = useState([]);

    useEffect(() => {
        const fetchApiData = async () => {
            if (!token) return null;

            try {
                const response = await axios(`${apiUrl}/exchange-api/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Token ${token}`,
                        'Content-Type': 'application/json'
                    },
                });
                if (response.status === 204) {
                    setNotification("Keine Einträge gefunden.");
                }

                setApiData2(response.data)
            } catch (e) {
                console.log("Error: ", e);
            }
        };
        fetchApiData();
    }, []);

    return (
       <div className="container mt-3 mb-3 fadeInDown animated">
           <div className="card shadow-bg col-md-9 mx-auto p-2">
               <div className="card-body">
                   <h2>Deine API-Schlüssel</h2>
               </div>

               <ListApiTable data={apiData2} />

               <div>
                   <button type="button" className="btn mb-3"
                           style={{backgroundColor: '#3A1CF3', color: 'white'}}
                           onClick={() => navigate('/user/api/add')}
                   >
                       API hinzufügen
                   </button>
               </div>

           </div>
       </div>
    );

}