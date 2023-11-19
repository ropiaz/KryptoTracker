import { createBrowserRouter } from "react-router-dom";
import UserLayout from "./components/UserLayout";
import GuestLayout from "./components/GuestLayout";
import NotFound from "./views/NotFound";
import Home from "./views/guest/Home";
import Login from "./views/guest/Login";
import Register from "./views/guest/Register";
import Dashboard from "./views/user/Dashboard";
import Settings from "./views/user/Settings";

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
        path: '/:username',
        element: <UserLayout />,
        children: [
            {
                path: '/:username',
                element: <Dashboard />
            },
            {
                path: '/:username/settings',
                element: <Settings />
            },
        ]
    },
    {
        path: '/*',
        element: <NotFound />
    }
]);

export default router;