import {useNavigate} from "react-router-dom";

export default function NotFound(){
    const navigate = useNavigate();
    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6 text-center">
                    <h1 className="display-3">404</h1>
                    <p className="lead">Die Seite konnte nicht gefunden werden.</p>
                    <p>Die von Ihnen angeforderte Seite existiert nicht oder wurde verschoben.</p>
                    <button onClick={() => {navigate('/')}} className="btn btn-primary">Zurück zur Startseite</button>
                </div>
            </div>
        </div>
    );
}
