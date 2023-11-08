import React from 'react';
import ReactDOM from 'react-dom/client';
import reportWebVitals from './reportWebVitals';
import {RouterProvider} from "react-router-dom";
import {ContextProvider} from "./contexts/ContextProvider";
import router from "./router.jsx";

import './index.css';
// Bootstrap 5.3.2 CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap 5.3.2 Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.min";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <ContextProvider>
            <RouterProvider router={router}/>
        </ContextProvider>
    </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
