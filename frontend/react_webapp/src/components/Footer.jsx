import React from 'react';
import { Link } from "react-router-dom";

export default function Footer(){
    // TODO: edit "to" to all Link tags
    return (
        <footer className="footer py-3">
            <div className="container">
                <div className="row">
                    <div className="col-md-4 text-white">
                        <h5>KRYPTOTRACKER</h5>
                        <ul className="list-unstyled">
                            <li><Link className="nav-link text-decoration-none" to='/'>Startseite</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Demoansicht</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Services</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>About & Team</Link></li>
                        </ul>
                    </div>
                    <div className="col-md-4 text-white">
                        <h5>HINWEISE</h5>
                        <ul className="list-unstyled">
                            <li><Link className="nav-link text-decoration-none" to='/'>News</Link></li>
                            <li><Link className="nav-link text-decoration-none" target="_blank" rel="noopener noreferrer" to={'https://github.com/ropiaz/KryptoTracker'}>GitHub</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Datenschutzbestimmungen</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Nutzungsbedingungen</Link></li>
                        </ul>
                    </div>
                    <div className="col-md-4 text-white">
                        <h5>SUPPORT</h5>
                        <ul className="list-unstyled">
                            <li><Link className="nav-link text-decoration-none" to='/'>Kontakt und FAQ</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Aktuelle Steuerrichtlinien</Link></li>
                            <li><Link className="nav-link text-decoration-none" to='/'>Unterstützte Krypto-Börsen und Wallets</Link></li>
                        </ul>
                    </div>
                </div>
            </div>
        </footer>
    );
}