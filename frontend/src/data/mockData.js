export const riskData = {
  building_id: "BLD-1024",
  risk_score: 82,
  risk_level: "HIGH",
  latitude: 17.3850,
  longitude: 78.4867
};

export const shelterData = {
  shelter_id: "SZ-001",
  name: "Community Hall",
  distance_km: 1.2,
  duration_min: 4,
  status: "Optimal"
};

export const routeData = {
  distance_km: 1.2,
  duration_min: 4,
  status: "Optimal"
};

export const responders = [
  {
    id: "R-001",
    name: "Responder 01",
    status: "Available"
  },
  {
    id: "R-002",
    name: "Responder 02",
    status: "On Mission"
  },
  {
    id: "R-003",
    name: "Responder 03",
    status: "Available"
  }
];

export const assistanceRequests = [
  {
    id: "REQ-101",
    location: "Old City Zone A",
    type: "Medical",
    status: "Pending"
  },
  {
    id: "REQ-102",
    location: "Market Road",
    type: "Rescue",
    status: "Assigned"
  },
  {
    id: "REQ-103",
    location: "Central Street",
    type: "Food",
    status: "Pending"
  }
];