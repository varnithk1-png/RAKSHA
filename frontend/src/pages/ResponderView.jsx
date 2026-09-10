import Header from "../components/Header.jsx";
import MapContainer from "../components/MapContainer.jsx";
import RiskPanel from "../components/RiskPanel.jsx";
import RoutePanel from "../components/RoutePanel.jsx";
import ResponderPanel from "../components/ResponderPanel.jsx";
import AssistancePanel from "../components/AssistancePanel.jsx";

function ResponderView({ onCitizenView }) {
  return (
    <div className="dashboard">

      <Header
        view="responder"
        onChangeView={onCitizenView}
      />

      <div className="responder-page">

        <div className="page-heading">

          <div>
            <h2>Responder Dashboard</h2>

            <p>
              Monitor incidents and coordinate emergency
              response.
            </p>
          </div>

          <div className="responder-online">
            🟢 Responder Network Online
          </div>

        </div>

        <div className="responder-map">
          <MapContainer />
        </div>

        <div className="responder-grid">

          <RiskPanel />

          <RoutePanel />

          <ResponderPanel />

          <AssistancePanel />

        </div>

      </div>

      <footer className="footer">
        <span>RAKSHA Disaster Response System</span>
        <span>Responder Operations</span>
        <span>System Operational</span>
      </footer>

    </div>
  );
}

export default ResponderView;