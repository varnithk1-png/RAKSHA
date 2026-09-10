import { useState } from "react";
import CitizenView from "./pages/CitizenView.jsx";
import ResponderView from "./pages/ResponderView.jsx";

function App() {
  const [view, setView] = useState("citizen");

  if (view === "responder") {
    return (
      <ResponderView
        onCitizenView={() => setView("citizen")}
      />
    );
  }

  return (
    <CitizenView
      onResponderView={() => setView("responder")}
    />
  );
}

export default App;