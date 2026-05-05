const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getAvailableShifts(token) {
  const res = await fetch(`${API_URL}/marketplace/shifts`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Failed to load marketplace shifts");
  return res.json();
}

export async function claimShift(token, shiftId) {
  const res = await fetch(`${API_URL}/marketplace/shifts/${shiftId}/claim`, {
    method: "POST",
    headers: authHeaders(token),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail ?? "Failed to claim shift");
  return body;
}

export async function requestDrop(token, shiftId) {
  const res = await fetch(`${API_URL}/marketplace/shifts/${shiftId}/drop`, {
    method: "POST",
    headers: authHeaders(token),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail ?? "Failed to submit drop request");
  return body;
}
