import { useEffect, useState, useRef } from "react";
import axios from "axios";
import { supabase } from "../lib/supabase";

const API = "http://localhost:8000/words";
const PAGE_SIZE = 10;

function AdminDashboard({ onBack }) {
  const [words, setWords] = useState([]);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState("all");
  const [session, setSession] = useState(null);

  // 🔥 stable function reference (NO RE-RENDER TRIGGERS)
  const fetchWordsRef = useRef(null);

  /* ---------------- SESSION ---------------- */
  useEffect(() => {
    const init = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session);
    };

    init();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, newSession) => setSession(newSession)
    );

    return () => listener.subscription.unsubscribe();
  }, []);

  /* ---------------- AUTH ---------------- */
  const getAuthHeader = () => {
    const email = session?.user?.email;
    return email ? { "x-user-email": email } : {};
  };

  /* ---------------- FETCH FUNCTION ---------------- */
  useEffect(() => {
    fetchWordsRef.current = async (pageNumber, statusFilter) => {
      const skip = pageNumber * PAGE_SIZE;

      let url = `${API}/admin?skip=${skip}&limit=${PAGE_SIZE}`;

      if (statusFilter !== "all") {
        url += `&status=${statusFilter}`;
      }

      try {
        const res = await axios.get(url, {
          headers: getAuthHeader(),
        });

        setWords(res.data.items);
        setTotal(res.data.total);
        setPage(pageNumber);
      } catch (err) {
        console.error(err);
      }
    };
  });

  /* ---------------- INITIAL LOAD ---------------- */
  useEffect(() => {
    if (!session) return;

    fetchWordsRef.current(0, filter);
  }, [session, filter]);

  /* ---------------- ACTIONS ---------------- */
  const updateStatus = async (id, status) => {
    await axios.patch(
      `${API}/admin/${id}/status?status=${status}`,
      null,
      { headers: getAuthHeader() }
    );

    fetchWordsRef.current(page, filter);
  };

  const deleteWord = async (word) => {
    if (!window.confirm("Delete this word?")) return;

    await axios.delete(`${API}/${word}`, {
      headers: getAuthHeader(),
    });

    fetchWordsRef.current(page, filter);
  };

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
            onClick={() => {
              setFilter(f);
              fetchWordsRef.current(0, f);
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* WORD LIST */}
      {words.map((w) => (
        <div key={w.id} style={{ borderBottom: "1px solid #ccc", padding: 10 }}>
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

      <div style={{ marginTop: 20 }}>
        Page {page + 1} / {Math.ceil(total / PAGE_SIZE)}
      </div>
    </div>
  );
}

export default AdminDashboard;