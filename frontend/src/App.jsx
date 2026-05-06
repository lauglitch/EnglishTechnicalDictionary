import { useEffect, useState } from "react";
import api from "./api/api";
import { supabase } from "./lib/supabase";

import AdminDashboard from "./pages/AdminDashboard";

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
      <h3 style={{ color: darkMode ? "#fff" : "#000" }}>{word.word}</h3>

      <p>{word.definition}</p>

      <button onClick={() => setOpen(!open)} style={{
                marginTop: 10,
                background: darkMode ? "#333" : "#f3f3f3",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #555" : "1px solid #ddd",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}>
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
  const [notFound, setNotFound] = useState(false);

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

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState(null);

  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  /* ---------------- LOGIN ---------------- */
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

    if (!data?.session) return;

    setSession(data.session);
  };

  /* ---------------- LOGOUT  ---------------- */
 const handleLogout = async () => {
    await supabase.auth.signOut();
    localStorage.removeItem("access_token");
    setSession(null);
    setShowAdmin(false);
    setNotFound(false);
  };
  

  /* ---------------- SESSION ---------------- */
  useEffect(() => {
    let mounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (mounted) setSession(data.session);
    });

    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (mounted) {
          setSession(session);

          // Prevents auto-return after logout
          if (!session) {
            setShowAdmin(false);
          }
        }
      }
    );

    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
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
      const res = await api.get(`/${search.toLowerCase()}`);

      setCurrentWord(res.data);
      setHasSearched(true);
      setMode("card");
      setRevealed(false);

      setNotFound(false);
    } catch {
      setCurrentWord(null);
      setHasSearched(true);
      setNotFound(true);
    }
  };

  /* ---------------- PAGINATION ---------------- */
  const loadPage = async (pageNumber = 0) => {
    const skip = pageNumber * PAGE_SIZE;

    const res = await api.get(`/?skip=${skip}&limit=${PAGE_SIZE}`);
    
    setWords(res.data.items);
    setTotal(res.data.total);
    setPage(pageNumber);
    setActiveLetter(null);

  };

  const loadLetterPage = async (letter, pageNumber = 0) => {
    const skip = pageNumber * PAGE_SIZE;

    const res = await api.get(
      `/letter/${letter.toLowerCase()}?skip=${skip}&limit=${PAGE_SIZE}`
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
    setPage(0);
    loadPage(0);
  };

  const hasMore = (page + 1) * PAGE_SIZE < total;

  /* ---------------- MODE SWITCH ---------------- */
  const toggleMode = async () => {
    setMode("book");
    setWords([]); // prevents A flash
    loadPage(0);
    setNotFound(false);

    if (mode === "card") {
      await loadPage(0);

      setActiveLetter(null); // no forced "A"
      setPage(0);
      setMode("book");

      loadPage(0); // load ALL instead of letter A
    } else {
      setMode("card");
      setWords([]);
      setActiveLetter(null);
      setPage(0);
    }
  };

  
  /* ---------------- UI ---------------- */
 return (
  <div>
    {showAdmin ? (
      !session ? (
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: darkMode ? "#111" : "#fff",
            padding: 16,
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: 340,
              padding: 20,
              borderRadius: 10,
              background: darkMode ? "#1a1a1a" : "#f5f5f5",
              boxSizing: "border-box",
            }}
          >
            <h2 style={{ color: darkMode ? "#fff" : "#111" }}>
              Admin Login
            </h2>

            <button
              onClick={() => {
                setShowAdmin(true);
                setNotFound(false);
              }}
              style={{
                width: "100%",
                marginBottom: 10,
                padding: 8,
                background: darkMode ? "#333" : "#eaeaea",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #555" : "1px solid #ddd",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              ← Back
            </button>

            <input
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%",
                marginBottom: 10,
                padding: 8,
                background: darkMode ? "#222" : "#fff",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #444" : "1px solid #ccc",
                borderRadius: 6,
              }}
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                marginBottom: 10,
                padding: 8,
                background: darkMode ? "#222" : "#fff",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #444" : "1px solid #ccc",
                borderRadius: 6,
              }}
            />

            <button
              onClick={handleLogin}
              style={{
                width: "100%",
                padding: 8,
                background: darkMode ? "#333" : "#f3f3f3",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #555" : "1px solid #ddd",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              Login
            </button>

            {authError && <p style={{ color: "red" }}>{authError}</p>}
          </div>
        </div>
      ) : (
        <AdminDashboard
          onBack={() => {
            setShowAdmin(false);
            setSearch("");
            setCurrentWord(null);
            setHasSearched(false);
            setRevealed(false);
          }}
          onLogout={handleLogout}
          darkMode={darkMode}
        />
      )
    ) : (
      <div
        style={{
          minHeight: "100vh",
          backgroundColor: darkMode ? "#111" : "#fff",
          color: darkMode ? "#fff" : "#000",
          display: "flex",
          justifyContent: "center",
          padding: 16,
          fontFamily: "Arial",
        }}
      >
        <div style={{ width: "100%", maxWidth: 900 }}>

          {/* TITLE */}
          <h1 style={{ color: darkMode ? "#fff" : "#3a3a3a" }}>
            📘 Technical Dictionary
          </h1>

          {/* TOP BUTTONS */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              marginBottom: 20,
              justifyContent: "center",
            }}
          >
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search word..."
              style={{
                flex: "1 1 160px",
                minWidth: 140,
                padding: 8,
                background: darkMode ? "#222" : "#fff",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #444" : "1px solid #ccc",
                borderRadius: 6,
              }}
            />

            <button
              onClick={handleSearch}
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
              onClick={toggleMode}
              style={{
                background: darkMode ? "#333" : "#f3f3f3",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #555" : "1px solid #ddd",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              {mode === "card" ? "📖 Book" : "🃏 Card"}
            </button>

            <button
              onClick={() => setDarkMode(!darkMode)}
              style={{
                background: darkMode ? "#333" : "#f3f3f3",
                color: darkMode ? "#fff" : "#111",
                border: darkMode ? "1px solid #555" : "1px solid #ddd",
                padding: "6px 10px",
                borderRadius: 6,
                cursor: "pointer",
              }}
            >
              {darkMode ? "☀️" : "🌙"}
            </button>

            <button
              onClick={() => {
                setStudyMode(!studyMode);
                setRevealed(false);
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
              {studyMode ? "👓" : "👁️"}
            </button>

            <button
              onClick={() => {
                setShowAdmin(true);
                setNotFound(false);
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
              🛠 Admin
            </button>
          </div>

          {/* BOOK MODE */}
          {mode === "book" ? (
            <div>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 6,
                  justifyContent: "center",
                }}
              >
                {alphabet.map((l) => (
                  <button
                    key={l}
                    onClick={() => handleLetterClick(l)}
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: "50%",
                      background: darkMode ? "#333" : "#f3f3f3",
                      color: darkMode ? "#fff" : "#111",
                      border: darkMode ? "1px solid #555" : "1px solid #ddd",
                    }}
                  >
                    {l}
                  </button>
                ))}

                <button
                  onClick={handleAllClick}
                  style={{
                    width: 60,
                    height: 40,
                    borderRadius: 20,
                    background: darkMode ? "#333" : "#f3f3f3",
                    color: darkMode ? "#fff" : "#111",
                    border: darkMode ? "1px solid #555" : "1px solid #ddd",
                  }}
                >
                  All
                </button>
              </div>

              <div style={{ marginTop: 10 }}>
                {words.map((w) => (
                  <BookItem key={w.id} word={w} darkMode={darkMode} />
                ))}
              </div>

              {/* PAGINATION */}
              <div style={{ marginTop: 20, textAlign: "center" }}>
                <button
                  disabled={page === 0}
                  onClick={() => {
                    const newPage = page - 1;
                    activeLetter
                      ? loadLetterPage(activeLetter, newPage)
                      : loadPage(newPage);
                  }}
                  style={{
                    background: darkMode ? "#333" : "#f3f3f3",
                    color: darkMode ? "#fff" : "#111",
                    border: darkMode ? "1px solid #555" : "1px solid #ddd",
                    padding: "6px 10px",
                    borderRadius: 6,
                  }}
                >
                  Prev
                </button>

                <span style={{ margin: "0 10px" }}>
                  Page {page + 1} / {Math.ceil(total / PAGE_SIZE)}
                </span>

                <button
                  disabled={!hasMore}
                  onClick={() => {
                    const newPage = page + 1;
                    activeLetter
                      ? loadLetterPage(activeLetter, newPage)
                      : loadPage(newPage);
                  }}
                  style={{
                    background: darkMode ? "#333" : "#f3f3f3",
                    color: darkMode ? "#fff" : "#111",
                    border: darkMode ? "1px solid #555" : "1px solid #ddd",
                    padding: "6px 10px",
                    borderRadius: 6,
                  }}
                >
                  Next
                </button>
              </div>
            </div>
          ) : (
            /* CARD VIEW */
            <div
              style={{
                borderBottom: "1px solid #444",
                padding: 12,
                background: darkMode ? "#1a1a1a" : "#f7f7f7",
                borderRadius: 10,
                marginTop: 10,
              }}
            >
              {notFound ? (
                <p style={{ color: "red" }}>Word not found</p>
              ) : !hasSearched || !currentWord ? (
                <p>📘 Search a word</p>
              ) : (
                <>
                  <h3>{currentWord.word}</h3>

                  {studyMode ? (
                  !revealed ? (
                    <p
                      onClick={() => setRevealed(true)}
                      style={{ cursor: "pointer", color: darkMode ? "#6ba0dc" : "#004cc6", marginBottom: 10}}
                    >
                      Click to reveal
                    </p>
                    ) : (
                      <>
                        <p
                          onClick={() => setRevealed(false)}
                          style={{ cursor: "pointer", color: darkMode ? "#6ba0dc" : "#004cc6", marginBottom: 10}}
                        >
                          Click to hide
                        </p>

                        <p style={{marginBottom: 10}}>{currentWord.definition}</p>
                        <p><b>Example:</b> {currentWord.example}</p>
                        <p><b>Grammar:</b> {currentWord.grammar_class}</p>
                        <p><b>Topic:</b> {currentWord.topic}</p>
                        <p><b>Author:</b> {currentWord.author}</p>
                      </>
                    )
                  ) : (
                    <div >
                      <p style={{marginBottom: 10}}>{currentWord.definition}</p>
                      <p><b>Example:</b> {currentWord.example}</p>
                      <p><b>Grammar:</b> {currentWord.grammar_class}</p>
                      <p><b>Topic:</b> {currentWord.topic}</p>
                      <p><b>Author:</b> {currentWord.author}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    )}
  </div>
);
}

export default App;