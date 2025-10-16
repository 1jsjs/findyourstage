export const API_BASE = import.meta.env.VITE_API_BASE;

export async function fetchToken() {
  const res = await fetch(`${API_BASE}/api/token`, { method: "POST" });
  if (!res.ok) throw new Error("token failed");
  return res.json();
}

export async function fetchPopConcerts({ stdate, eddate, page = 1, rows = 20 }) {
  const { token } = await fetchToken();
  const url = new URL(`${API_BASE}/api/concerts`);
  url.searchParams.set("stdate", stdate);
  url.searchParams.set("eddate", eddate);
  url.searchParams.set("cpage", String(page));
  url.searchParams.set("rows", String(rows));

  const res = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("concerts failed");
  return res.json();
}
