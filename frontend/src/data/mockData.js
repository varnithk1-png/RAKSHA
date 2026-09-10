// Mock/demo data for Task 2 frontend development.
// Actual risk, safe-zone, routing and assistance data will come
// from the common FastAPI backend during final integration.

export const riskData = {
  building_id: "BLD-1024",
  risk_score: 82,
  risk_level: "High",
  latitude: 17.3850,
  longitude: 78.4867
};

export const shelterData = {
  shelter_id: "SZ-001",
  name: "Community Hall",
  latitude: 17.3875,
  longitude: 78.4880,
  capacity: 200,
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
    responder_id: "R-001",
    name: "Responder 01",
    latitude: 17.3860,
    longitude: 78.4875,
    status: "Available"
  },
  {
    responder_id: "R-002",
    name: "Responder 02",
    latitude: 17.3835,
    longitude: 78.4855,
    status: "On Mission"
  },
  {
    responder_id: "R-003",
    name: "Responder 03",
    latitude: 17.3845,
    longitude: 78.4890,
    status: "Available"
  }
];

export const assistanceRequests = [
  {
    id: "REQ-101",
    building_id: "BLD-1024",
    latitude: 17.3850,
    longitude: 78.4867,
    location: "Old City Zone A",
    type: "Medical",
    status: "Pending"
  },
  {
    id: "REQ-102",
    building_id: "BLD-1025",
    latitude: 17.3838,
    longitude: 78.4858,
    location: "Market Road",
    type: "Rescue",
    status: "Assigned"
  },
  {
    id: "REQ-103",
    building_id: "BLD-1026",
    latitude: 17.3862,
    longitude: 78.4892,
    location: "Central Street",
    type: "Food",
    status: "Pending"
  }
];