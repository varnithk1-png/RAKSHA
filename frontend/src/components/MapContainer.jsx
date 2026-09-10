function MapContainer() {
  return (
    <div className="map-container">

      <div className="map-toolbar">

        <div>
          🗺️ Risk Map
        </div>

        <div className="map-controls">
          <button>+</button>
          <button>−</button>
          <button>⛶</button>
        </div>

      </div>

      <div className="map-area">

        <div className="map-grid"></div>

        <div className="road road-1"></div>
        <div className="road road-2"></div>
        <div className="road road-3"></div>
        <div className="road road-4"></div>

        <div className="risk-zone risk-high"></div>
        <div className="risk-zone risk-medium"></div>
        <div className="risk-zone risk-low"></div>

        <div className="map-marker victim">
          📍
          <span>Victim</span>
        </div>

        <div className="map-marker responder responder-1">
          🚑
          <span>Responder</span>
        </div>

        <div className="map-marker responder responder-2">
          🚑
        </div>

        <div className="safe-zone-marker">
          🟢
          <span>Safe Zone 1</span>
        </div>

        <div className="route-line"></div>

        <div className="road-block">
          🚧
        </div>

        <div className="map-label label-1">
          Old City Zone A
        </div>

        <div className="map-label label-2">
          Market Road
        </div>

        <div className="map-label label-3">
          Community Hall
        </div>

      </div>

    </div>
  );
}

export default MapContainer;