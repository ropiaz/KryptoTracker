import { useQuery } from 'react-query';
import { useStateContext } from '../contexts/ContextProvider';

export const getTransactions = () => {
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchTransactions = async () => {
        if (!token) return null;

        try {
            const response = await fetch(`${apiUrl}/transaction/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
            });
            if (!response.ok) {
                setNotification("Keine Verbindung zum Datenbankserver. Bitte später erneut versuchen.");
                throw new Error('Netzwerkantwort war nicht ok.');
            }
            return await response.json();
        } catch (e) {
            console.log("Error: ", e);
        }
    };

    const { data: transactionData, error, isLoading, isError } = useQuery(
        ['getTransactions', token],
        fetchTransactions,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 60, // Die Daten bleiben für 60 Minuten frisch
            cacheTime: 1000 * 60 * 60, // Cache-Zeit von 60 Minuten
        }
    );

    return { transactionData, isLoading, isError, error };
};

export const getTransactionTypes = () => {
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchTransactionTypes = async () => {
        if (!token) return null;

        try {
            const response = await fetch(`${apiUrl}/transaction-type/`, {
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                },
            });
            if (!response.ok) {
                setNotification("Keine Verbindung zum Datenbankserver. Bitte später erneut versuchen.");
                throw new Error('Netzwerkantwort war nicht ok.');
            }
            return await response.json();
        } catch (e) {
            console.log("Error: ", e);
        }
    };

    const { data: transactionTypeData, error, isLoading, isError } = useQuery(
        ['getTransactionTypes', token],
        fetchTransactionTypes,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 60, // Die Daten bleiben für 60 Minuten frisch
            cacheTime: 1000 * 60 * 60, // Cache-Zeit von 60 Minuten
        }
    );

    return { transactionTypeData, isLoading, isError, error };
};