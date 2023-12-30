import { useQuery } from 'react-query';
import { useStateContext } from '../contexts/ContextProvider';

export const getPortfolio = () => {
    const { token } = useStateContext();
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
                console.log(response);
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
            staleTime: 1000 * 60 * 60, // Die Daten bleiben für 60 Minuten frisch
            cacheTime: 1000 * 60 * 60, // Cache-Zeit von 60 Minuten
        }
    );

    return { portfolioData, isLoading, isError, error };
};