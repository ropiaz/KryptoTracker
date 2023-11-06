import { createBrowserRouter } from "react-router-dom";
import GuestLayout from "./components/GuestLayout";
import NotFound from "./views/NotFound";
import Home from "./views/guest/Home";

const router = createBrowserRouter([
    {
        path: '/',
        element: <GuestLayout />,
        children: [
            {
                path: '/',
                element: <Home />
            },
        ]
    },
    {
        path: '/*',
        element: <NotFound />
    }
]);

export default router;