import { useState } from "react";

function AssistancePanel() {
  const [message, setMessage] = useState("");

  function sendWhatsApp() {
    setMessage(
      "WhatsApp assistance request initiated."
    );
  }

  function sendSOS() {
    setMessage(
      "🚨 SOS request sent successfully."
    );
  }

  return (
    <section className="panel">

      <div className="panel-title">
        <span>🆘</span>
        <h3>Emergency Help</h3>
      </div>

      <div className="help-buttons">

        <button
          className="whatsapp-button"
          onClick={sendWhatsApp}
        >
          💬 WhatsApp
        </button>

        <button
          className="sos-button"
          onClick={sendSOS}
        >
          🚨 SOS
        </button>

      </div>

      {message && (
        <div className="help-message">
          {message}
        </div>
      )}

    </section>
  );
}

export default AssistancePanel;