import { riskData } from "../data/mockData.js";

function RiskPanel() {
  return (
    <section className="panel">

      <div className="panel-title">
        <span>⚠️</span>
        <h3>Risk Summary</h3>
      </div>

      <div className="risk-summary">

        <div className="risk-circle">
          <strong>{riskData.risk_score}</strong>
          <span>/100</span>
        </div>

        <div className="risk-details">
          <span className="risk-level">
            {riskData.risk_level}
          </span>

          <p>Current Area Risk</p>
        </div>

      </div>

      <div className="area-info">

        <div>
          <span>Building ID</span>
          <strong>{riskData.building_id}</strong>
        </div>

        <div>
          <span>Population Exposure</span>
          <strong>Demo</strong>
        </div>

        <div>
          <span>Building Vulnerability</span>
          <strong>Demo</strong>
        </div>

      </div>

    </section>
  );
}

export default RiskPanel;