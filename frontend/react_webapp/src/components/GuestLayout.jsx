import { Outlet } from "react-router-dom";
import Header from "./Header";
import Footer from "./Footer";

export default function GuestLayout(){
    return (
        <div id="guestlayout">
            <Header />
            <main>
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}
