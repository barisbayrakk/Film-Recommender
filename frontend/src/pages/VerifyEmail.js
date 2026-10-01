
import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";
import "./Auth.css"; 

function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState("Verifying...");
    const navigate = useNavigate();

    useEffect(() => {
        const token = searchParams.get("token");
        if (!token) {
            setStatus("❌ Invalid link. No token found.");
            return;
        }

        async function verify() {
            try {
                const data = await apiFetch(`/auth/verify-email?token=${token}`, {
                    method: "GET",
                });
                setStatus(`✅ ${data.msg}`);

                
                setTimeout(() => {
                    navigate("/login");
                }, 3000);

            } catch (err) {
                setStatus(`❌ Verification failed: ${err.detail || "Unknown error"}`);
            }
        }

        verify();
    }, [searchParams, navigate]);

    return (
        <div className="auth-background">
            <div className="auth-card" style={{ textAlign: "center" }}>
                <h1 className="auth-title">Email Verification</h1>
                <p className={`auth-message ${status.includes("✅") ? "success" : "error"}`}>
                    {status}
                </p>
                {status.includes("✅") && <p>Redirecting to login...</p>}
            </div>
        </div>
    );
}

export default VerifyEmail;
