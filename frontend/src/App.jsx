import { useEffect, useState } from "react";
import axios from "axios";
import { supabase } from "./lib/supabase";

import AdminDashboard from "./pages/AdminDashboard";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/words";
const PAGE_SIZE = 3;

/* ---------------- BOOK ITEM ---------------- */
function BookItem({ word, darkMode }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      style={{
        borderBottom: "1px solid #444",
        padding: "12px",
        background: darkMode ? "#1a1a1a" : "#f7f7f7",
        borderRadius: "10px",
        marginBottom: "10px",
      }}
    >
      <h3 style={{ color: darkMode ? "#fff" : "#000" }}>
        {word.word}
      </h3>

      <p>{word.definition}</p>

      <button onClick={() => setOpen(!open)} style={{ marginTop: 8 }}>
        {open ? "Hide" : "More"}
      </button>

      {open && (
        <div style={{ marginTop: 10, fontSize: 14 }}>
          <p><b>Grammar:</b> {word.grammar_class || "-"}</p>
          <p><b>Topic:</b> {word.topic || "-"}</p>
          <p><b>Example:</b> {word.example || "-"}</p>
          <p><b>Author:</b> {word.author || "-"}</p>
        </div>
      )}
    </div>
  );
}

/* ---------------- MAIN APP ---------------- */
function App() {
  const [words, setWords] = useState([]);
  const [currentWord, setCurrentWord] = useState(null);
  const [search, setSearch] = useState("");

  const [revealed, setRevealed] = useState(false);
  const [mode, setMode] = useState("card");
  const [darkMode, setDarkMode] = useState(true);

  const [hasSearched, setHasSearched] = useState(false);
  const [studyMode, setStudyMode] = useState(true);

  const [page, setPage] = useState(0);
  const [activeLetter, setActiveLetter] = useState(null);
  const [total, setTotal] = useState(0);

  const [showAdmin, setShowAdmin] = useState(false);

  const [session, setSession] = useState(null);
  const [loadingSession, setLoadingSession] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState(null);
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);

  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  /* ---------------- SESSION ---------------- */
  const handleLogin = async () => {
  setAuthError(null);

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    setAuthError(error.message);
    return;
  }

  if (data.session) {
    setIsAdminAuthenticated(true);
  }
};

  useEffect(() => {
    const getSession = async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session);
      setLoadingSession(false);
    };

    getSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        setSession(newSession);
        setLoadingSession(false);
      }
    );

    return () => listener.subscription.unsubscribe();
  }, []);

  /* ---------------- STYLE ---------------- */
  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? "#111" : "#fff";
    document.body.style.margin = "0";
  }, [darkMode]);

  /* ---------------- SEARCH ---------------- */
  const handleSearch = async () => {
    if (!search) return;

    try {
      const res = await axios.get(`${API}/${search.toLowerCase()}`);

      setCurrentWord(res.data);
      setHasSearched(true);
      setMode("card");
      setRevealed(false);
    } catch {
      alert("Word not found");
    }
  };

  /* ---------------- LOAD PAGE ---------------- */
  const loadPage = async (pageNumber = 0) => {
    const skip = pageNumber * PAGE_SIZE;

    const res = await axios.get(`${API}?skip=${skip}&limit=${PAGE_SIZE}`);

    setWords(res.data.items);
    setTotal(res.data.total);
    setPage(pageNumber);
    setActiveLetter(null);
  };

  /* ---------------- LOAD LETTER ---------------- */
  const loadLetterPage = async (letter, pageNumber = 0) => {
    const skip = pageNumber * PAGE_SIZE;

    const res = await axios.get(
      `${API}/letter/${letter.toLowerCase()}?skip=${skip}&limit=${PAGE_SIZE}`
    );

    setWords(res.data.items);
    setTotal(res.data.total);
    setPage(pageNumber);
  };

  const handleLetterClick = (letter) => {
    setActiveLetter(letter);
    loadLetterPage(letter, 0);
  };

  const handleAllClick = () => {
    setActiveLetter(null);
    loadPage(0);
  };

  /* ---------------- MODE SWITCH (FIXED START A) ---------------- */
  const toggleMode = async () => {
    if (mode === "card") {
      await loadPage(0);
      setActiveLetter("A");   // 🔥 FORCE START FROM A
      setPage(0);
      setMode("book");
      loadLetterPage("A", 0);
    } else {
      setMode("card");
      setWords([]);
      setActiveLetter(null);
      setPage(0);
    }
  };

  const hasMore = (page + 1) * PAGE_SIZE < total;

  /* ---------------- UI ---------------- */
  return (
    <div>
      {showAdmin ? (
      !isAdminAuthenticated ? (
        /* ---------------- LOGIN PAGE ---------------- */
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: darkMode ? "#111" : "#fff",
          }}
        >
          <div
            style={{
              width: 320,
              padding: 20,
              borderRadius: 10,
              background: darkMode ? "#1a1a1a" : "#f5f5f5",
            }}
          >
            <h2 style={{ color: darkMode ? "#fff" : "#000" }}>
              Admin Login
            </h2>

            <input
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: "100%", marginBottom: 10 }}
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", marginBottom: 10 }}
            />

            <button
              onClick={handleLogin}
              style={{ width: "100%" }}
            >
              Login
            </button>

            {authError && (
              <p style={{ color: "red" }}>{authError}</p>
            )}
          </div>
        </div>
      ) : (
        /* ---------------- ADMIN DASHBOARD ---------------- */
        <AdminDashboard onBack={() => {
          setShowAdmin(false);
          setIsAdminAuthenticated(false);
        }} />
      )
    ) : (
        <div
          style={{
            minHeight: "100vh",
            backgroundColor: darkMode ? "#111" : "#fff",
            color: darkMode ? "#fff" : "#000",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: 20,
            fontFamily: "Arial",
          }}
        >
          {/* 🔥 FIX TITLE VISIBILITY IN LIGHT MODE */}
          <h1 style={{ color: darkMode ? "#fff" : "#111" }}>
            📘 Technical Dictionary
          </h1>

          {/* CONTROLS */}
          <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search word..."
            />

            <button onClick={handleSearch}>Search</button>

            <button onClick={toggleMode}>
              {mode === "card" ? "📖 Book" : "🃏 Card"}
            </button>

            <button onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? "☀️" : "🌙"}
            </button>

            <button onClick={() => setStudyMode(!studyMode)}>
              {studyMode ? "👁️" : "👓"}
            </button>

            <button
              onClick={() => {
                setShowAdmin(true);
                setIsAdminAuthenticated(false); // always force login first
              }}
            >
              {showAdmin ? "📘 App" : "🛠 Admin"}
            </button>
          </div>

          {/* ADMIN STATUS */}
          {showAdmin && loadingSession && <p>Loading session...</p>}

         {showAdmin && !loadingSession && !session && (
            <div
              style={{
                width: "100%",
                maxWidth: 300,
                marginTop: 20,
                padding: 15,
                border: "1px solid #444",
                borderRadius: 10,
                background: darkMode ? "#1a1a1a" : "#f5f5f5",
              }}
            >
              <h3 style={{ color: darkMode ? "#fff" : "#000" }}>
                Admin Login
              </h3>

              <input
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ width: "100%", marginBottom: 10 }}
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ width: "100%", marginBottom: 10 }}
              />

              <button onClick={handleLogin} style={{ width: "100%" }}>
                Login
              </button>

              {authError && (
                <p style={{ color: "red", marginTop: 10 }}>
                  {authError}
                </p>
              )}
            </div>
          )}

          {/* BOOK MODE */}
          {mode === "book" ? (
            <div style={{ width: "100%", maxWidth: 700 }}>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {alphabet.map((l) => (
                  <button key={l} onClick={() => handleLetterClick(l)}>
                    {l}
                  </button>
                ))}
                <button onClick={handleAllClick}>All</button>
              </div>

              {words.map((w) => (
                <BookItem key={w.id} word={w} darkMode={darkMode} />
              ))}

              <div style={{ marginTop: 20 }}>
                <button disabled={page === 0}
                  onClick={() => {
                    const newPage = page - 1;
                    activeLetter
                      ? loadLetterPage(activeLetter, newPage)
                      : loadPage(newPage);
                  }}
                >
                  Prev
                </button>

                <span>
                  Page {page + 1} / {Math.ceil(total / PAGE_SIZE)}
                </span>

                <button disabled={!hasMore}
                  onClick={() => {
                    const newPage = page + 1;
                    activeLetter
                      ? loadLetterPage(activeLetter, newPage)
                      : loadPage(newPage);
                  }}
                >
                  Next
                </button>
              </div>
            </div>
          ) : (
            /* ---------------- CARD MODE (FIXED WRAP ADDED) ---------------- */
            <div style={{ width: "100%", maxWidth: 700 }}>
              <div
                style={{
                  borderBottom: "1px solid #444",
                  padding: "12px",
                  background: darkMode ? "#1a1a1a" : "#f7f7f7",
                  borderRadius: "10px",
                  marginTop: 10,
                }}
              >
                {!hasSearched || !currentWord ? (
                  <p>📘 Search a word</p>
                ) : (
                  <>
                    <h3 style={{ color: darkMode ? "#fff" : "#000" }}>
                      {currentWord.word}
                    </h3>

                    {studyMode && !revealed ? (
                      <p onClick={() => setRevealed(true)}>
                        Click to reveal
                      </p>
                    ) : (
                      <>
                        <p>{currentWord.definition}</p>
                        <p><b>Example:</b> {currentWord.example}</p>
                        <p><b>Grammar:</b> {currentWord.grammar_class}</p>
                        <p><b>Topic:</b> {currentWord.topic}</p>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;