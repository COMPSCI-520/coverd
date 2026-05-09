const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getRequests(token, statusFilter = null) {
  const url = new URL(`${API_URL}/manager/requests`);
  if (statusFilter) url.searchParams.set("status", statusFilter);

  const res = await fetch(url.toString(), { headers: authHeaders(token) });

  if (!res.ok) throw new Error("Failed to load requests");

  return res.json();
}

export async function approveRequest(token, requestId) {
  const res = await fetch(`${API_URL}/manager/requests/${requestId}/approve`, {
    method: "POST",
    headers: authHeaders(token),
  });

  const body = await res.json();

  if (!res.ok) throw new Error(body.detail ?? "Failed to approve request");

  return body;
}

export async function denyRequest(token, requestId) {
  const res = await fetch(`${API_URL}/manager/requests/${requestId}/deny`, {
    method: "POST",
    headers: authHeaders(token),
  });

  const body = await res.json();

  if (!res.ok) throw new Error(body.detail ?? "Failed to deny request");

  return body;
}

export async function getStudentRequests(token) {
  const res = await fetch(`${API_URL}/students/me/requests`, {
    headers: authHeaders(token),
  });

  if (!res.ok) throw new Error("Failed to load your requests");

  return res.json();
}

export async function getStaffSchedule(token, filters = {}) {
  const url = new URL(`${API_URL}/manager/staff-schedule`);

  if (filters.weekStart) url.searchParams.set("week_start", filters.weekStart);
  if (filters.location && filters.location !== "All locations") {
    url.searchParams.set("location", filters.location);
  }
  if (filters.student) url.searchParams.set("student", filters.student);

  const res = await fetch(url.toString(), {
    headers: authHeaders(token),
  });

  if (!res.ok) throw new Error("Failed to load staff schedule");

  return res.json();
}