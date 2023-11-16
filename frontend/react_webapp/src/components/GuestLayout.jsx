import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";
import { useStateContext } from "../contexts/ContextProvider";

export default function GuestLayout(){
    const { notification } = useStateContext();

    return (
        <div id="guestlayout">
            <Header />
            <main>
                <Outlet />
            </main>
            {notification &&
                <div className="notification">
                    {notification}
                </div>
            }
            <Footer />
        </div>
    );
}
