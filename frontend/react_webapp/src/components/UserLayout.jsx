import React from "react";
import { Outlet } from "react-router-dom";
import Footer from "./Footer";

// import { useStateContext } from "../contexts/ContextProvider";
// import AdminLogin from "../views/admin/Login";
// import AdminHeader from "../views/admin/Header";

export default function UserLayout(){
    // const {token, setToken} = useStateContext();
    //
    // const [isTokenValid, setIsTokenValid] = useState(false);
    //
    // useEffect(() => {
    //     async function checkToken() {
    //         try {
    //             const response = await fetch(`http://localhost:3030/auth/check/${token}`, {
    //                 method: 'GET',
    //             });
    //
    //             if (!response.ok && response.status === 403) {
    //                 setIsTokenValid(false);
    //                 setToken(null);
    //             } else {
    //                 setIsTokenValid(true);
    //             }
    //         } catch (error) {
    //             setIsTokenValid(false);
    //             setToken(null);
    //         }
    //     }
    //
    //     if (token) {
    //         checkToken();
    //     }
    // }, [token]);
    //
    // if (!isTokenValid) {
    //     return <AdminLogin />;
    // }

    return (
        <div id="userlayout">
            {/*<AdminHeader />*/}
            <main>
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}