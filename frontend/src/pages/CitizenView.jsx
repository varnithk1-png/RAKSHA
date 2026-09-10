import Header from "../components/Header.jsx";
import MapContainer from "../components/MapContainer.jsx";
import RiskPanel from "../components/RiskPanel.jsx";
import SafeZonePanel from "../components/SafeZonePanel.jsx";
import RoutePanel from "../components/RoutePanel.jsx";
import AssistancePanel from "../components/AssistancePanel.jsx";
import ResponderPanel from "../components/ResponderPanel.jsx";
import { assistanceRequests } from "../data/mockData.js";

function CitizenView({ onResponderView }) {
  return (
    <div className="dashboard">

      <Header
        view="citizen"
        onChangeView={onResponderView}
      />

      <div className="dashboard-body">

        <aside className="sidebar">

          <div className="sidebar-section">
            <h4>Main Menu</h4>

            <button className="sidebar-item active">
              🏠 Dashboard
            </button>

            <button className="sidebar-item">
              🗺️ Risk Map
            </button>

            <button className="sidebar-item">
              🟢 Safe Zones
            </button>

            <button className="sidebar-item">
              🧭 Evacuation
            </button>

            <button className="sidebar-item">
              🆘 Help / SOS
            </button>

            <button
              className="sidebar-item"
              onClick={onResponderView}
            >
              🚑 Responder View
            </button>
          </div>

          <div className="sidebar-section">

            <h4>Map Layers</h4>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Risk Areas
            </label>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Safe Zones
            </label>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Victim Location
            </label>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Responders
            </label>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Routes
            </label>

            <label>
              <input
                type="checkbox"
                defaultChecked
              />
              Road Blocks
            </label>

          </div>

          <div className="sidebar-section legend">

            <h4>Risk Legend</h4>

            <div>
              <span className="legend-color high"></span>
              High Risk
            </div>

            <div>
              <span className="legend-color medium"></span>
              Medium Risk
            </div>

            <div>
              <span className="legend-color low"></span>
              Low Risk
            </div>

            <div>
              <span className="legend-color safe"></span>
              Safe Zone
            </div>

          </div>

        </aside>

        <main className="main-content">

          <div className="page-heading">

            <div>
              <h2>Disaster Response Dashboard</h2>

              <p>
                Monitor risk, safety zones and evacuation
                routes.
              </p>
            </div>

            <div className="location-status">
              📍 Old City Zone A
            </div>

          </div>

          <MapContainer />

          <div className="dashboard-grid">

            <RiskPanel />

            <SafeZonePanel />

            <RoutePanel />

          </div>

        </main>

        <aside className="right-panel">

          <AssistancePanel />

          <section className="panel">

            <div className="panel-title">
              <span>📋</span>
              <h3>Recent Requests</h3>
            </div>

            <div className="request-list">

              {assistanceRequests.map((request) => (
                <div
                  className="request-item"
                  key={request.id}
                >

                  <div>
                    <strong>{request.type}</strong>
                    <span>{request.location}</span>
                  </div>

                  <small
                    className={
                      request.status.toLowerCase()
                    }
                  >
                    {request.status}
                  </small>

                </div>
              ))}

            </div>

          </section>

          <ResponderPanel />

        </aside>

      </div>

      <footer className="footer">
        <span>RAKSHA Disaster Response System</span>
        <span>Task 2 — Frontend</span>
        <span>System Operational</span>
      </footer>

    </div>
  );
}

export default CitizenView;