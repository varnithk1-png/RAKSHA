import { shelterData } from "../data/mockData.js";

function SafeZonePanel() {
  return (
    <section className="panel">

      <div className="panel-title">
        <span>🟢</span>
        <h3>Safe Zone</h3>
      </div>

      <div className="safe-zone-card">

        <div className="safe-zone-icon">
          🏢
        </div>

        <div className="safe-zone-info">

          <h4>{shelterData.name}</h4>

          <p>{shelterData.shelter_id}</p>

          <div className="safe-zone-stats">
            <span>
              📍 {shelterData.distance_km} km
            </span>

            <span>
              ⏱ {shelterData.duration_min} min
            </span>
          </div>

        </div>

        <span className="optimal">
          {shelterData.status}
        </span>

      </div>

    </section>
  );
}

export default SafeZonePanel;