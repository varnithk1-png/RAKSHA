import { routeData } from "../data/mockData.js";

function RoutePanel() {
  return (
    <section className="panel">

      <div className="panel-title">
        <span>🧭</span>
        <h3>Evacuation Route</h3>
      </div>

      <div className="route-preview">

        <div className="route-point">

          <span className="point current"></span>

          <div>
            <strong>Current Location</strong>
            <small>Old City Zone A</small>
          </div>

        </div>

        <div className="route-connector"></div>

        <div className="route-point">

          <span className="point destination"></span>

          <div>
            <strong>Safe Zone 1</strong>
            <small>Community Hall</small>
          </div>

        </div>

      </div>

      <div className="route-stats">

        <div>
          <span>Distance</span>
          <strong>
            {routeData.distance_km} km
          </strong>
        </div>

        <div>
          <span>Duration</span>
          <strong>
            {routeData.duration_min} min
          </strong>
        </div>

        <div>
          <span>Status</span>
          <strong className="optimal">
            {routeData.status}
          </strong>
        </div>

      </div>

    </section>
  );
}

export default RoutePanel;