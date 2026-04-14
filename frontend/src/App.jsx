import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000/words";
const PAGE_SIZE = 3;

/* ---------------- BOOK ITEM COMPONENT ---------------- */
function BookItem({ word, darkMode }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      style={{
        borderBottom: "1px solid #444",
        padding: "12px 0",
      }}
    >
      <h3 style={{ color: darkMode ? "#fff" : "#111" }}>
        {word.word}
      </h3>

      <p>{word.definition}</p>

      <button
        onClick={() => setOpen(!open)}
        style={{
          marginTop: "8px",
          fontSize: "12px",
          cursor: "pointer",
        }}
      >
        {open ? "Hide" : "More"}
      </button>

      {open && (
        <div style={{ marginTop: "10px", fontSize: "14px" }}>
          <p><b>Grammar:</b> {word.grammar_class || "-"}</p>
          <p><b>Topic:</b> {word.topic || "-"}</p>
          <p><b>Example:</b> {word.example || "-"}</p>
          <p><b>Author:</b> {word.author}</p>
          <p><b>Status:</b> {word.status}</p>
        </div>
      )}
    </div>
  );
}

/* ---------------- MAIN APP ---------------- */
function App() {
  const [words, setWords] = useState([]);
  const [index, setIndex] = useState(0);

  const [currentWord, setCurrentWord] = useState(null);
  const [search, setSearch] = useState("");

  const [revealed, setRevealed] = useState(false);
  const [mode, setMode] = useState("card");
  const [darkMode, setDarkMode] = useState(true);

  const [hasSearched, setHasSearched] = useState(false);
  const [studyMode, setStudyMode] = useState(true);

  const [page, setPage] = useState(0);

  const current = words.length > 0 ? words[index] : null;
  current;
  
  /* ---------------- BODY BACKGROUND FIX ---------------- */
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

  /* ---------------- LOAD BOOK PAGE ---------------- */
  const loadPage = async (pageNumber = 0) => {
    try {
      const skip = pageNumber * PAGE_SIZE;

      const res = await axios.get(
        `${API}/?skip=${skip}&limit=${PAGE_SIZE}`
      );

      const sorted = res.data.sort((a, b) =>
        a.word.toLowerCase().localeCompare(b.word.toLowerCase())
      );

      setWords(sorted);
      setPage(pageNumber);
      setIndex(0);
      setRevealed(false);
    } catch (err) {
      console.error(err);
    }
  };

  /* ---------------- MODE SWITCH ---------------- */
  const toggleMode = async () => {
    if (mode === "card") {
      await loadPage(0);
      setMode("book");
    } else {
      setMode("card");
      setWords([]);
      setIndex(0);
    }
  };

  /* ---------------- KEYBOARD (BOOK MODE ONLY) ---------------- */
  useEffect(() => {
    const handleKey = (e) => {
      if (mode !== "book") return;
      if (!words.length) return;

      if (e.code === "Space") {
        e.preventDefault();
        setRevealed((r) => !r);
      }

      if (e.key === "ArrowRight") {
        setIndex((i) => Math.min(i + 1, words.length - 1));
        setRevealed(false);
      }

      if (e.key === "ArrowLeft") {
        setIndex((i) => Math.max(i - 1, 0));
        setRevealed(false);
      }
    };

    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [mode, words]);

  /* ---------------- UI ---------------- */
  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: darkMode ? "#111" : "#fff",
        color: darkMode ? "#fff" : "#000",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        fontFamily: "Arial",
        paddingTop: "40px",
      }}
    >
      {/* TITLE */}
      <h1 style={{ color: darkMode ? "#fff" : "#111" }}>
        📘 Technical Dictionary
      </h1>

      {/* CONTROLS */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search word..."
        />

        <button onClick={handleSearch}>Search</button>

        <button onClick={toggleMode}>
          {mode === "card" ? "📖 Book Mode" : "🃏 Card Mode"}
        </button>

        <button onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>

        <button onClick={() => setStudyMode(!studyMode)}>
          {studyMode ? "👁️ Study ON" : "👓 Study OFF"}
        </button>
      </div>

      {/* BOOK MODE */}
      {mode === "book" ? (
        <div
          style={{
            width: "100%",
            display: "flex",
            justifyContent: "center",
          }}
        >
          <div style={{ maxWidth: "700px", width: "100%", padding: "0 20px" }}>
            {words.map((w, i) => (
              <BookItem key={i} word={w} darkMode={darkMode} />
            ))}

            {/* PAGINATION */}
            <div
              style={{
                marginTop: "20px",
                display: "flex",
                justifyContent: "center",
                gap: "12px",
                alignItems: "center",
              }}
            >
              <button
                onClick={() => loadPage(page - 1)}
                disabled={page === 0}
              >
                ⬅️ Prev
              </button>

              <span>Page {page + 1}</span>

              <button onClick={() => loadPage(page + 1)}>
                Next ➡️
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* CARD MODE */
        <div
          style={{
            border: "1px solid #333",
            padding: "40px",
            borderRadius: "12px",
            maxWidth: "500px",
            width: "100%",
            backgroundColor: darkMode ? "#222" : "#fff",
            textAlign: "center",
          }}
        >
          {!hasSearched || !currentWord ? (
            <p style={{ color: "#aaa", fontSize: "18px" }}>
              📘 Use the search bar to discover interesting words
            </p>
          ) : (
            <div>
              <h2 style={{ fontSize: "30px" }}>
                {currentWord.word}
              </h2>

              {studyMode ? (
                !revealed ? (
                  <p
                    onClick={() => setRevealed(true)}
                    style={{ color: "#888", cursor: "pointer" }}
                  >
                    Click or press SPACE to reveal
                  </p>
                ) : (
                  <>
                    <p>{currentWord.definition}</p>
                    <hr />
                    <p><b>Example:</b> {currentWord.example || "-"}</p>
                    <p><b>Grammar:</b> {currentWord.grammar_class || "-"}</p>
                    <p><b>Topic:</b> {currentWord.topic || "-"}</p>
                    <p><b>Author:</b> {currentWord.author}</p>
                    <p><b>Status:</b> {currentWord.status}</p>
                  </>
                )
              ) : (
                <>
                  <p><b>Definition:</b> {currentWord.definition}</p>
                  <p><b>Example:</b> {currentWord.example || "-"}</p>
                  <p><b>Grammar:</b> {currentWord.grammar_class || "-"}</p>
                  <p><b>Topic:</b> {currentWord.topic || "-"}</p>
                  <p><b>Author:</b> {currentWord.author}</p>
                  <p><b>Status:</b> {currentWord.status}</p>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;