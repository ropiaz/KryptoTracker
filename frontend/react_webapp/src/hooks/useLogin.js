import {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';
import { useStateContext } from '../contexts/ContextProvider';
import axios from 'axios';

export default function useLogin(){
    const { setUser, setToken } = useStateContext();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const handleLogin = async (event) => {
        event.preventDefault();

        try {
            setErrorMessage('');
            if(email !== '' && password !== '') {
                axios.post("http://localhost:8000/api/login/",
                    {
                        email: email,
                        password: password
                    },
                    {
                        xsrfCookieName: 'csrftoken',
                        xsrfHeaderName: 'X-CSRFToken',
                        headers: {'Content-Type': 'application/json'}
                    }
                )
                    .then((res) => {
                        setErrorMessage('');
                        const userData = res.data.detail;
                        const token = res.data.token;
                        setToken(token);
                        setUser(userData);

                        setEmail('');
                        setPassword('');
                        setTimeout(() => {
                            navigate(`/${userData.username}`);
                        }, 1000);
                    })
                    .catch((error) => {
                        let msg = "";
                        for (const errorKey in error.response.data) {
                            console.log(error.response.data[errorKey])
                            msg = msg + `${error.response.data[errorKey]} \n`;
                        }
                        setErrorMessage(msg);
                    });
            } else {
                setErrorMessage('Bitte das Loginformular ausfüllen.');
            }
        } catch (err) {
            console.log('Fehler beim Login: ', err);
            setErrorMessage("Fehler beim Login.");
        }
    };

    useEffect(() => {
        if (password === "") {
            setPassword("");
        }
        if (email === "") {
            setEmail("");
        }
        if (errorMessage === "") {
            setErrorMessage("");
        }
    }, [email, password, errorMessage]);

    return {
        email,
        setEmail,
        password,
        setPassword,
        errorMessage,
        setErrorMessage,
        handleLogin
    };
};