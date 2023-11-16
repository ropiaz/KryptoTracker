import {createContext, useContext, useState} from "react";

const StateContext = createContext({
  token: null,
  notification: null,
  setToken: () => {},
  setNotification: () => {}
});

export const ContextProvider = ({children}) => {
  const [token, _setToken] = useState(localStorage.getItem('ACCESS_TOKEN'));
  const [notification, _setNotification] = useState('');

  const setNotification = (message) => {
    _setNotification(message);
    setTimeout(() => {
      _setNotification('')
    }, 2500);
  }

  const setToken = (token) => {
    _setToken(token);
    if(token) {
      localStorage.setItem('ACCESS_TOKEN', token);
    } else {
      localStorage.removeItem('ACCESS_TOKEN');
    }
  }

  return (
    <StateContext.Provider value={{
      token,
      notification,
      setToken,
      setNotification,
    }}>
      {children}
    </StateContext.Provider>
  );
}

export const useStateContext = () => useContext(StateContext);
