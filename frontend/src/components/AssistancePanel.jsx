import { useState } from "react";

function AssistancePanel() {
  const [message, setMessage] = useState("");

  function sendWhatsApp() {
    setMessage("WhatsApp assistance request initiated.");
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