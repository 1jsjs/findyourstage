import { useEffect, useState } from "react";
import { fetchPopConcerts } from "./lib/api";

export default function App() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        // 날짜 형식: YYYYMMDD
        const res = await fetchPopConcerts({
          stdate: "20251001",
          eddate: "20251031",
          rows: 12,
        });
        setItems(res?.items ?? []);
      } catch (e) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div style={{padding:16}}>불러오는 중…</div>;
  if (err) return <div style={{padding:16, color:"crimson"}}>에러: {err}</div>;

return (
  <div style={{padding: 16, display: "flex", flexDirection: "column", alignItems: "center"}}>
    <h1 style={{marginBottom: 12}}>find your stage</h1>
    {items.length === 0 ? (
      <div>검색 결과가 없습니다.</div>
    ) : (
      <ul
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 24,
          listStyle: "none",
          padding: 0,
          justifyContent: "center", // 💡 그리드 가운데 정렬
          maxWidth: 1600,           // 💡 중앙 영역 제한
        }}
      >
        {items.map(it => (
          <li key={it.mt20id} style={{
            border: "1px solid #eee",
            borderRadius: 12,
            padding: 12,
            background: "#fff",
            boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
          }}>
            {it.poster && (
              <img
                src={it.poster}
                alt={it.prfnm}
                style={{
                  width: "100%",
                  borderRadius: 8,
                  objectFit: "cover",
                }}
              />
            )}
            <div style={{marginTop: 8, fontWeight: 600}}>{it.prfnm}</div>
            <div style={{fontSize: 13, color: "#555"}}>{it.fcltynm}</div>
            <div style={{fontSize: 13}}>
              {it.prfpdfrom} ~ {it.prfpdto}
            </div>
          </li>
        ))}
      </ul>
    )}
  </div>
);
}