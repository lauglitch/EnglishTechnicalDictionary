import { useEffect, useState } from "react";
import api from "../api/api";
import { supabase } from "../lib/supabase";

const PAGE_SIZE = 10;

function AdminDashboard({ onBack, onLogout = () => {}, darkMode }) {
  const [words, setWords] = useState([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState("all");
  const [session, setSession] = useState(null);

  const [query, setQuery] = useState({
    page: 0,
    filter: "all",
  });

  /* ---------------- SEARCH ---------------- */
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");

  const displayedWords = appliedSearch
    ? words.filter(
        (w) => w.word.toLowerCase() === appliedSearch.toLowerCase()
      )
    : words;

  /* ---------------- SESSION ---------------- */
  useEffect(() => {
    let mounted = true;

    const initSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (mounted) setSession(data.session);
    };

    initSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        if (mounted) setSession(newSession);
      }
    );
    
    return () => {
      mounted = false;
      listener?.subscription?.unsubscribe?.();
    };
  }, []);

  const getToken = () => session?.access_token?.trim() || null;

  /* ---------------- FETCH ---------------- */
  useEffect(() => {
    const token = session?.access_token;

    if (!session || !token) return;

    const controller = new AbortController();

    const fetchWords = async () => {
      const skip = query.page * PAGE_SIZE;

      let url = `/admin/list?skip=${skip}&limit=${PAGE_SIZE}`;

      if (query.filter !== "all") {
        url += `&status=${query.filter}`;
      }

      try {
        const res = await api.get(url, {
          signal: controller.signal,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const items = res.data?.items ?? [];
        const total = res.data?.total ?? 0;

        setWords(items);
        setTotal(total);

        setFilter(query.filter);
      } catch (err) {
        if (err.name !== "CanceledError") {
          console.error("ADMIN FETCH ERROR:", err);
        }
      }
    };

    fetchWords();

    return () => controller.abort();
  }, [session, query]);

  useEffect(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth", 
    });
  }, [query.page, query.filter]);

  /* ---------------- RELOAD ---------------- */
  const reload = (newPage = query.page, newFilter = filter) => {
    setQuery({
      page: newPage,
      filter: newFilter,
    });
  };

  /* ---------------- ACTIONS ---------------- */
  const updateStatus = async (id, status) => {
    const token = getToken();
    if (!token) return;

    try {
      await api.patch(
        `/admin/status/${id}?status=${status}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      reload(query.page, filter);
    } catch (err) {
      console.error("UPDATE STATUS ERROR:", err);
    }
  };

  const deleteWord = async (word) => {
    const token = getToken();
    if (!token) return;

    if (!window.confirm("Delete this word?")) return;

    try {
      await api.delete(`/admin/${word}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      reload(query.page, filter);
    } catch (err) {
      console.error("DELETE ERROR:", err);
    }
  };
  

  const hasMore = (query.page + 1) * PAGE_SIZE < total;

  const start = total === 0 ? 0 : query.page * PAGE_SIZE + 1;

  const end = Math.min(
    (query.page + 1) * PAGE_SIZE,
    total
  );

  /* ---------------- UI ---------------- */
return (
  <div>
    <h1 style={{ color: darkMode ? "#fff" : "#111", textAlign: "center" }}>
      Admin Dashboard
    </h1>

    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 10,
        marginBottom: 15,
      }}
    >
      <button
        onClick={onBack}
        style={{
          background: darkMode ? "#333" : "#f2f2f2",
          color: darkMode ? "#fff" : "#111",
          border: darkMode ? "1px solid #555" : "1px solid #ddd",
          padding: "6px 12px",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        ⬅ Back
      </button>

      <button
        onClick={onLogout}
        style={{
          background: "red",
          color: "#fff",
          border: "none",
          padding: "6px 12px",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </div>

    {!session && <p style={{ color: "red" }}>Loading session...</p>}

    {/* FILTERS */}
    <div
      style={{
        marginBottom: 20,
        display: "flex",
        justifyContent: "center",
        gap: 10,
        flexWrap: "wrap",
      }}
    >
      {["All", "Pending", "Approved", "Rejected"].map((f) => (
        <button
          key={f}
          onClick={() => reload(0, f.toLowerCase())}
          style={{
            fontWeight: filter === f.toLowerCase() ? "bold" : "normal",
            minWidth: 90,
            textAlign: "center",
            background: darkMode ? "#333" : "#f5f5f5",
            color: darkMode ? "#fff" : "#111",
            border: darkMode ? "1px solid #555" : "1px solid #ddd",
            padding: "6px 10px",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          {f}
        </button>
      ))}
    </div>

    {/* SEARCH */}
    <div
      style={{
        marginBottom: 15,
        display: "flex",
        justifyContent: "center",
        gap: 10,
        flexWrap: "wrap",
        alignItems: "center",
      }}
    >
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search word..."
        style={{
          padding: 8,
          marginRight: 8,
          background: darkMode ? "#222" : "#fafafa",
          color: darkMode ? "#fff" : "#111",
          border: darkMode ? "1px solid #444" : "1px solid #ccc",
          borderRadius: 6,
        }}
      />

      <button
        onClick={() => setAppliedSearch(search)}
        style={{
          background: darkMode ? "#333" : "#f3f3f3",
          color: darkMode ? "#fff" : "#111",
          border: darkMode ? "1px solid #555" : "1px solid #ddd",
          padding: "6px 10px",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        Search
      </button>

      <button
        onClick={() => {
          setSearch("");
          setAppliedSearch("");
        }}
        style={{
          background: darkMode ? "#333" : "#f3f3f3",
          color: darkMode ? "#fff" : "#111",
          border: darkMode ? "1px solid #555" : "1px solid #ddd",
          padding: "6px 10px",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
        Clear
      </button>
    </div>

    {/* WORD LIST */}
    {appliedSearch ? (
      displayedWords.length === 1 ? (
        displayedWords.map((w) => (
          <div
            key={w.id}
            style={{
              borderBottom: "1px solid #ccc",
              padding: 10,
              color: darkMode ? "#ddd" : "#111",
            }}
          >
            <h3 style={{ color: darkMode ? "#fff" : "#111" }}>{w.word}</h3>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Definition: {w.definition}</p>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Example: {w.example}</p>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Grammar: {w.grammar_class}</p>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Topic: {w.topic}</p>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Author: {w.author}</p>
            <p style={{ color: darkMode ? "#bbb" : "#333" }}>Status: {w.status}</p>
          </div>
        ))
      ) : (
        <p>No data found</p>
      )
    ) : words.length === 0 ? (
      <p>No data</p>
    ) : (
      words.map((w) => (
        <div
          key={w.id}
          style={{
            borderBottom: "1px solid #ccc",
            padding: 10,
            color: darkMode ? "#ddd" : "#111",
          }}
        >
          <h3 style={{ color: darkMode ? "#fff" : "#111" }}>{w.word}</h3>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Definition: {w.definition}</p>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Example: {w.example}</p>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Grammar: {w.grammar_class}</p>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Topic: {w.topic}</p>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Author: {w.author}</p>
          <p style={{ color: darkMode ? "#bbb" : "#333" }}>Status: {w.status}</p>

          <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
            <button
              onClick={() => updateStatus(w.id, "approved")}
              style={{
                background: "#2e7d32",
                color: "#fff",
                border: "1px solid #2e7d32",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              Approve
            </button>

            <button
              onClick={() => updateStatus(w.id, "rejected")}
              style={{
                background: "#c62828",
                color: "#fff",
                border: "1px solid #c62828",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              Reject
            </button>

            <button
              onClick={() => deleteWord(w.word)}
              style={{
                background: darkMode ? "#333" : "#fafafa",
                color: "#b00020",
                border: "1px solid #b00020",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              Delete
            </button>
          </div>
        </div>
      ))
    )}

    {/* PAGINATION */}
    {!appliedSearch && (
      <div style={{ marginTop: 20, marginBottom: 40 }}>
        <button
          disabled={query.page === 0}
          onClick={() => reload(query.page - 1, filter)}
          style={{
            background: darkMode ? "#333" : "#ffffff",
            color: darkMode ? "#fff" : "#111",
            border: darkMode ? "1px solid #555" : "1px solid #ccc",
            padding: "6px 10px",
            borderRadius: 6,
            cursor: "pointer",
            opacity: query.page === 0 ? 0.5 : 1,
          }}
        >
          Prev
        </button>

        <span style={{ margin: "0 10px", color: darkMode ? "#ddd" : "#111" }}>
          Showing {start}–{end} / {total} — Page{" "}
          {total === 0 ? 0 : query.page + 1} / {Math.ceil(total / PAGE_SIZE)}
        </span>

        <button
          disabled={!hasMore}
          onClick={() => reload(query.page + 1, filter)}
          style={{
            background: darkMode ? "#333" : "#ffffff",
            color: darkMode ? "#fff" : "#111",
            border: darkMode ? "1px solid #555" : "1px solid #ccc",
            padding: "6px 10px",
            borderRadius: 6,
            cursor: "pointer",
            opacity: !hasMore ? 0.5 : 1,
          }}
        >
          Next
        </button>
      </div>
    )}
  </div>
);
}

export default AdminDashboard;