import React, { useState } from "react";
import axios from "axios";
import { useNavigate, useParams } from "react-router-dom";

// TODO: edit and update transaction data
// edit transaction component
export default function EditTransaction() {
    const {id} = useParams();
    console.log(id);

    return (
        <div className="container mt-3 mb-3 fadeInDown animated">
            <div className="card shadow-bg col-md-9 mx-auto">
                <div className="card-body">
                    <h2>Transaktion bearbeiten</h2>
                </div>
            </div>
        </div>
    );
}