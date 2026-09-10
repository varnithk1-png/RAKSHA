import { responders } from "../data/mockData.js";

function ResponderPanel() {
  return (
    <section className="panel">

      <div className="panel-title">
        <span>🚑</span>
        <h3>Active Responders</h3>
      </div>

      <div className="responder-list">

        {responders.map((responder) => (
          <div
            className="responder-item"
            key={responder.id}
          >

            <div className="responder-avatar">
              🚑
            </div>

            <div className="responder-info">
              <strong>{responder.name}</strong>
              <span>{responder.id}</span>
            </div>

            <span
              className={
                responder.status === "Available"
                  ? "responder-status available"
                  : "responder-status mission"
              }
            >
              {responder.status}
            </span>

          </div>
        ))}

      </div>

    </section>
  );
}

export default ResponderPanel;