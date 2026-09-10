const API_BASE_URL = "http://localhost:8000";

export async function getRiskData() {
  const response = await fetch(`${API_BASE_URL}/risk`);

  if (!response.ok) {
    throw new Error("Failed to fetch risk data");
  }

  return response.json();
}

export async function getSafeZones() {
  const response = await fetch(`${API_BASE_URL}/safe-zones`);

  if (!response.ok) {
    throw new Error("Failed to fetch safe zones");
  }

  return response.json();
}

export async function getRoute(latitude, longitude) {
  const response = await fetch(
    `${API_BASE_URL}/route?latitude=${latitude}&longitude=${longitude}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch route");
  }

  return response.json();
}

export async function sendAssistanceRequest(requestData) {
  const response = await fetch(
    `${API_BASE_URL}/assistance`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requestData)
    }
  );

  if (!response.ok) {
    throw new Error("Failed to send assistance request");
  }

  return response.json();
}