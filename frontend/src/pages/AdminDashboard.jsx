import { useEffect, useState, useCallback } from "react";
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

  const getToken = useCallback(() => session?.access_token || null, [session]);

  /* ---------------- SESSION ---------------- */
  useEffect(() => {
    let mounted = true;

    const initSession = async () => {
      const { data, error } = await supabase.auth.getSession();

      if (!error && mounted) {
        setSession(data.session);
      }
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

  /* ---------------- FETCH ---------------- */
  useEffect(() => {
    const token = getToken();
    if (!token) return;

    const controller = new AbortController();

    const fetchWords = async () => {
      const skip = query.page * PAGE_SIZE;

      let url = `/admin?skip=${skip}&limit=${PAGE_SIZE}`;

      if (query.filter !== "all") {
        url += `&status=${query.filter}`;
      }

      try {
        console.log("ADMIN EMAIL USED:", session?.user?.email);
        console.log("TOKEN BEING SENT:", session.access_token);

        const res = await api.get(url, {
          signal: controller.signal,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        setWords(res.data?.items ?? []);
        setTotal(res.data?.total ?? 0);

        setPage(query.page);
        setFilter(query.filter);
      } catch (err) {
        if (err?.name === "CanceledError" || err?.code === "ERR_CANCELED") return;
        console.error("ADMIN FETCH ERROR:", err);
      }
    };

    fetchWords();

    return () => controller.abort();
  }, [session, query.page, query.filter, getToken]);

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
      await api.patch(
        `/admin/${id}/status?status=${status}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

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
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      reload(page, filter);
    } catch (err) {
      console.error("DELETE ERROR:", err);
    }
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