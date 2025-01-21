import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { verifyEmail } from "../../services/authService";

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setError("Invalid verification link.");
        return;
      }
      try {
        const response = await verifyEmail(token);
        setMessage(response.message);
      } catch (err) {
        setError(err.detail || "Verification failed.");
      }
    };
    verify();
  }, [token]);

  return (
    <div>
      <h2>Email Verification</h2>
      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default VerifyEmail;