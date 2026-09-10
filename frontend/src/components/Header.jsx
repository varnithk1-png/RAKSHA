function Header({ view, onChangeView }) {
  return (
    <header className="header">

      <div className="brand">
        <div className="brand-icon">🛡️</div>

        <div>
          <h1>RAKSHA</h1>
          <span>Disaster Response System</span>
        </div>
      </div>

      <nav className="top-nav">
        <button className="nav-item active">
          Dashboard
        </button>

        <button className="nav-item">
          Risk Analysis
        </button>

        <button className="nav-item">
          Safe Zones
        </button>

        <button className="nav-item">
          Evacuation
        </button>

        <button className="nav-item">
          Responders
        </button>

        <button className="nav-item">
          Requests
        </button>
      </nav>

      <div className="header-actions">

        <div className="system-status">
          <span className="status-dot"></span>
          System Operational
        </div>

        <button className="notification-button">
          🔔
        </button>

        <button
          className="view-button"
          onClick={onChangeView}
        >
          {view === "citizen"
            ? "Responder View"
            : "Citizen View"}
        </button>

      </div>

    </header>
  );
}

export default Header;