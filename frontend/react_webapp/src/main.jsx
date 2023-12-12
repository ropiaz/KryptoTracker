import React from 'react';
import ReactDOM from 'react-dom/client';
import {RouterProvider} from "react-router-dom";
import {ContextProvider} from "./contexts/ContextProvider";
import router from "./router.jsx";

import './index.css';
// Bootstrap 5.3.2 CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap 5.3.2 Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.min";

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ContextProvider>
            <RouterProvider router={router}/>
        </ContextProvider>
    </React.StrictMode>,
)
