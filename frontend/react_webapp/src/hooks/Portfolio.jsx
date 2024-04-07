import { useQuery } from 'react-query';
import { useStateContext } from '../contexts/ContextProvider';

export const getDashboard = () => {
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchDashboard = async () => {
        if (!token) return null;

        try {
            const response = await fetch(`${apiUrl}/dashboard/`, {
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

    const { data: dashboardData, error, isLoading, isError } = useQuery(
        ['getDashboard', token],
        fetchDashboard,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 30, // Die Daten bleiben für 30 Minuten frisch
            cacheTime: 1000 * 60 * 30, // Cache-Zeit von 30 Minuten
        }
    );

    return { dashboardData, isLoading, isError, error };
};

export const getPortfolio = () => {
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchPortfolio = async () => {
        if (!token) return null;

        try {
            const response = await fetch(`${apiUrl}/portfolio/`, {
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

    const { data: portfolioData, error, isLoading, isError } = useQuery(
        ['getPortfolio', token],
        fetchPortfolio,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 5, // Die Daten bleiben für 5 Minuten frisch
            cacheTime: 1000 * 60 * 5, // Cache-Zeit von 5 Minuten
        }
    );

    return { portfolioData, isLoading, isError, error };
};

export const getPortfolioType = () => {
    const { token, setNotification } = useStateContext();
    const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/api`;

    const fetchPortfolioType = async () => {
        if (!token) return null;

        try {
            const response = await fetch(`${apiUrl}/portfolio-type/`, {
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

    const { data: portfolioTypeData, error, isLoading, isError } = useQuery(
        ['getPortfolioType', token],
        fetchPortfolioType,
        {
            enabled: !!token, // Führt die Abfrage nur aus, wenn ein Token vorhanden ist
            staleTime: 1000 * 60 * 60, // Die Daten bleiben für 60 Minuten frisch
            cacheTime: 1000 * 60 * 60, // Cache-Zeit von 60 Minuten
        }
    );

    return { portfolioTypeData, isLoading, isError, error };
};