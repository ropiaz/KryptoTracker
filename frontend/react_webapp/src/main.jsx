import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { RouterProvider } from "react-router-dom";
import { ContextProvider } from "./contexts/ContextProvider";
import router from "./router.jsx";

import './index.css';
// Bootstrap 5.3.2 CSS
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
// Bootstrap 5.3.2 Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.min";
// import App from "./App.jsx";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <QueryClientProvider client={queryClient}>
            <ContextProvider>
                <RouterProvider router={router}/>
            </ContextProvider>
        </QueryClientProvider>
    </React.StrictMode>,
)
