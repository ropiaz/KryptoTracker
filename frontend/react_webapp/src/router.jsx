import { createBrowserRouter } from "react-router-dom";
import UserLayout from "./components/UserLayout";
import GuestLayout from "./components/GuestLayout";
import NotFound from "./views/NotFound";
import Home from "./views/guest/Home";
import Login from "./views/guest/Login";
import Register from "./views/guest/Register";
import Dashboard from "./views/dashboard/Dashboard";
import Settings from "./views/user/Settings";
import Tax from "./views/tax/Tax";
import AddAsset from "./views/dashboard/AddAsset.jsx";
import AddPortfolio from "./views/dashboard/AddPortfolio.jsx";
import Transaction from "./views/transaction/Transaction.jsx";
import AddTransaction from "./views/transaction/AddTransaction.jsx";
import DataImport from "./views/transaction/DataImport.jsx";
import EditTransaction from "./views/transaction/EditTransaction.jsx";
import AddAPI from "./views/exchange-api/AddApi.jsx";
import ShowApi from "./views/exchange-api/ShowApi.jsx";


const router = createBrowserRouter([
    {
        path: '/',
        element: <GuestLayout />,
        children: [
            {
                path: '/',
                element: <Home />
            },
            {
                path: '/login',
                element: <Login />
            },
            {
                path: '/register',
                element: <Register />
            },
        ]
    },
    {
        path: '/user',
        element: <UserLayout />,
        children: [
            {
                path: '/user/dashboard',
                element: <Dashboard />
            },
            {
                path: '/user/settings',
                element: <Settings />
            },
            {
                path: '/user/taxes',
                element: <Tax />
            },
            {
                path: '/user/transactions',
                element: <Transaction />,
            },
            {
                path: '/user/transactions/add',
                element: <AddTransaction />,
            },
            {
                path: '/user/transactions/edit/:id',
                element: <EditTransaction />,
            },
            {
                path: '/user/transactions/import',
                element: <DataImport />,
            },
            {
                path: '/user/portfolio/add',
                element: <AddPortfolio />
            },
            {
                path: '/user/asset/add',
                element: <AddAsset />
            },
            {
                path: '/user/api',
                element: <ShowApi />
            },
            {
                path: '/user/api/add',
                element: <AddAPI />
            },
        ]
    },
    {
        path: '/*',
        element: <NotFound />
    }
]);

export default router;