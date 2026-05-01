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

    const initSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (mounted) {
        // console.log("SESSION INIT:", data.session);
        setSession(data.session);
      }
    };

    initSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        // console.log("SESSION CHANGE:", newSession);
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
    const token = getToken();

    if (!token) {
      console.log("ERROR: NO TOKEN");
      return;
    }

    const controller = new AbortController();

    const fetchWords = async () => {
      const skip = query.page * PAGE_SIZE;

      let url = `/admin?skip=${skip}&limit=${PAGE_SIZE}`;
      if (query.filter !== "all") {
        url += `&status=${query.filter}`;
      }

      // console.log("FETCH:", url);

      try {
        const res = await api.get(url, {
          signal: controller.signal,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        // console.log("RESPONSE:", res.data);

        const items = res.data?.items ?? [];
        const total = res.data?.total ?? 0;

        // console.log("ITEMS:", items.length);

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
      await api.patch(`/admin/${id}/status?status=${status}`,
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

  const hasMore = (page + 1) * PAGE_SIZE < total;

  /* ---------------- UI ---------------- */
  return (
    <div style={{ padding: 20 }}>
      <h1>Admin Dashboard</h1>

      <button onClick={onBack}>⬅ Back</button>

      {!session && (
        <p style={{ color: "red" }}>
          Loading session...
        </p>
      )}

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
      {words.length === 0 ? (
        <p>No data</p>
      ) : (
        words.map((w) => (
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
        ))
      )}

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