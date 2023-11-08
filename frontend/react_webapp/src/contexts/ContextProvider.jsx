import {createContext, SetStateAction, useContext, useState} from "react";

const StateContext = createContext({
  user: null,
  token: null,
  setUser: user => {},
  setToken: number => {},
});

export const ContextProvider = ({children}) => {
  const [token, _setToken] = useState(localStorage.getItem('ACCESS_TOKEN'));
  const [user, _setUser] = useState({});

  const setToken = (token) => {
    _setToken(token);
    if(token) {
      localStorage.setItem('ACCESS_TOKEN', token);
    } else {
      localStorage.removeItem('ACCESS_TOKEN');
    }
  }

  const setUser = (user) => {
    _setUser(user);
  }

  return (
    <StateContext.Provider value={{
      user,
      token,
      setUser,
      setToken,
    }}>
      {children}
    </StateContext.Provider>
  );
}

export const useStateContext = () => useContext(StateContext);
