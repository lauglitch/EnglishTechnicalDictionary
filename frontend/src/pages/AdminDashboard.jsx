import { useEffect, useState } from "react";
import api from "../api/api";
import { supabase } from "../lib/supabase";

const PAGE_SIZE = 10;

function AdminDashboard({ onBack }) {
  const [words, setWords] = useState([]);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState("all");
  const [session, setSession] = useState(null);

  const [query, setQuery] = useState({
    page: 0,
    filter: "all",
  });

  /* ---------------- SESSION ---------------- */
  useEffect(() => {
    let mounted = true;

    const init = async () => {
      const { data } = await supabase.auth.getSession();
      if (mounted) setSession(data.session);
    };

    init();

    const { data } = supabase.auth.onAuthStateChange((_event, newSession) => {
      if (mounted) setSession(newSession);
    });

    // ✅ FIX: correct cleanup
    return () => {
      mounted = false;
      data.subscription?.unsubscribe();
    };
  }, []);

  /* ---------------- FETCH ---------------- */
  useEffect(() => {
    if (!session?.user?.email) return;

    const controller = new AbortController();

    const fetchWords = async () => {
      const skip = query.page * PAGE_SIZE;

      let url = `/admin?skip=${skip}&limit=${PAGE_SIZE}`;

      if (query.filter !== "all") {
        url += `&status=${query.filter}`;
      }

      try {
        console.log("ADMIN EMAIL USED:", session.user.email);

        const res = await api.get(url, {
          signal: controller.signal,
        });

        setWords(res.data?.items || []);
        setTotal(res.data?.total || 0);
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
    if (!session?.user?.email) return;

    await api.patch(`/admin/${id}/status?status=${status}`);

    reload(page, filter);
  };

  const deleteWord = async (word) => {
    if (!session?.user?.email) return;

    if (!window.confirm("Delete this word?")) return;

    api.delete(`/${word}`)

    reload(page, filter);
  };

  /* ---------------- PAGINATION ---------------- */
  const hasMore = (page + 1) * PAGE_SIZE < total;

  /* ---------------- UI ---------------- */
  return (
    <div style={{ padding: 20 }}>
      <h1>Admin Dashboard</h1>

      <button onClick={onBack}>⬅ Back</button>

      {!session && <p style={{ color: "red" }}>Not logged in</p>}

      {/* FILTERS */}
      <div style={{ marginBottom: 20 }}>
        {["all", "pending", "approved", "rejected"].map((f) => (
          <button
            key={f}
            onClick={() => reload(0, f)}
            style={{
              marginRight: 5,
              fontWeight: filter === f ? "bold" : "normal",
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* WORD LIST */}
      {(words || []).map((w) => (
        <div
          key={w.id}
          style={{ borderBottom: "1px solid #ccc", padding: 10 }}
        >
          <h3>{w.word}</h3>
          <p>{w.definition}</p>
          <p>Status: {w.status}</p>

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
      ))}

      {/* PAGINATION */}
      <div style={{ marginTop: 20 }}>
        <button disabled={page === 0} onClick={() => reload(page - 1, filter)}>
          Prev
        </button>

        <span style={{ margin: "0 10px" }}>
          Page {page + 1} / {Math.ceil(total / PAGE_SIZE)}
        </span>

        <button disabled={!hasMore} onClick={() => reload(page + 1, filter)}>
          Next
        </button>
      </div>
    </div>
  );
}

export default AdminDashboard;