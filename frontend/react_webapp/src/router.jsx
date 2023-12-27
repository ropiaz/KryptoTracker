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
        ]
    },
    {
        path: '/*',
        element: <NotFound />
    }
]);

export default router;