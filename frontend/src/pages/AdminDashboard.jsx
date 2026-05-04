import { useEffect, useState } from "react";
import api from "../api/api";
import { supabase } from "../lib/supabase";

const PAGE_SIZE = 10;

function AdminDashboard({ onBack, onLogout = () => {}, darkMode }) {
  const [words, setWords] = useState([]);
  const [page, setPage] = useState(0);
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
    console.log(token)
    if (!session || !token) return;

    const controller = new AbortController();

    const fetchWords = async () => {
      const skip = query.page * PAGE_SIZE;

      let url = `/admin?skip=${skip}&limit=${PAGE_SIZE}`;

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

        setPage(query.page);
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

  /* ---------------- RELOAD ---------------- */
  const reload = (newPage = page, newFilter = filter) => {
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
      await api.patch(`/admin/${id}/status?status=${status}`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      reload(page, filter);
    } catch (err) {
      console.error("UPDATE STATUS ERROR:", err);
    }
  };

  const deleteWord = async (word) => {
    const token = getToken();
    if (!token) return;

    if (!window.confirm("Delete this word?")) return;

    try {
      await api.delete(`/${word}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      reload(page, filter);
    } catch (err) {
      console.error("DELETE ERROR:", err);
    }
  };
  

  const hasMore = (page + 1) * PAGE_SIZE < total;

  /* ---------------- UI ---------------- */
  return (
    <div>
      <h1 style={{ color: darkMode ? "#fff" : "#000", textAlign: "center" }}>
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
        <button onClick={onBack}>
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
          style={{ padding: 6, marginRight: 8 }}
        />

        <button onClick={() => setAppliedSearch(search)}>
          Search
        </button>

        <button
          onClick={() => {
            setSearch("");
            setAppliedSearch("");
          }}
        >
          Clear
        </button>
      </div>

      {/* WORD LIST */}
      {appliedSearch ? (
        displayedWords.length === 1 ? (
          displayedWords.map((w) => (
            <div key={w.id} style={{ borderBottom: "1px solid #ccc", padding: 10 }}>
              <h3>{w.word}</h3>
              <p>{w.definition}</p>
              <p>Status: {w.status}</p>
            </div>
          ))
        ) : (
          <p>No data found</p>
        )
      ) : words.length === 0 ? (
        <p>No data</p>
      ) : (
        words.map((w) => (
          <div key={w.id} style={{ borderBottom: "1px solid #ccc", padding: 10 }}>
            <h3>{w.word}</h3>
            <p>{w.definition}</p>
            <p>Status: {w.status}</p>

            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button onClick={() => updateStatus(w.id, "approved")}>
                Approve
              </button>

              <button onClick={() => updateStatus(w.id, "rejected")}>
                Reject
              </button>

              <button onClick={() => deleteWord(w.word)}>
                Delete
              </button>
            </div>
          </div>
        ))
      )}

      {/* PAGINATION */}
      {!appliedSearch && (
        <div style={{ marginTop: 20 }}>
          <button disabled={page === 0} onClick={() => reload(page - 1, filter)}>
            Prev
          </button>

          <span style={{ margin: "0 10px" }}>
            Showing {words.length} / {total} — Page {page + 1} /{" "}
            {Math.ceil(total / PAGE_SIZE)}
          </span>

          <button disabled={!hasMore} onClick={() => reload(page + 1, filter)}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;