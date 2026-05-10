const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function authHeaders(token) {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function getMySchedule(token, month, year) {
  const url = new URL(`${API_URL}/students/me/schedule`);

  url.searchParams.set("month", month);
  url.searchParams.set("year", year);

  const response = await fetch(url.toString(), {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch schedule");
  }

  return response.json();
}