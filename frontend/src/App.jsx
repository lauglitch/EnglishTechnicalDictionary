import { useEffect, useState } from "react";
import axios from "axios";

const API =
  import.meta.env.VITE_API_URL || "http://localhost:8000/words";
const PAGE_SIZE = 3;

/* ---------------- BOOK ITEM ---------------- */
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

  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  /* ---------------- BODY ---------------- */
  useEffect(() => {
    document.body.style.backgroundColor = darkMode ? "#111" : "#fff";
    document.body.style.margin = "0";
  }, [darkMode]);

  /* ---------------- PARSER ---------------- */
  const parseResponse = (res) => {
    const data = res.data;

    const list = data?.items || [];
    const total = data?.total ?? 0;

    return { list, total };
  };

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

    const res = await axios.get(
      `${API}/?skip=${skip}&limit=${PAGE_SIZE}`
    );

    const { list, total } = parseResponse(res);

    setWords(list);
    setTotal(total);
    setPage(pageNumber);
    setActiveLetter(null);
  };

  /* ---------------- LOAD LETTER ---------------- */
  const loadLetterPage = async (letter, pageNumber = 0) => {
    const skip = pageNumber * PAGE_SIZE;

    const res = await axios.get(
      `${API}/letter/${letter.toLowerCase()}?skip=${skip}&limit=${PAGE_SIZE}`
    );

    const { list, total } = parseResponse(res);

    setWords(list);
    setTotal(total);
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

  const toggleMode = async () => {
    if (mode === "card") {
      await loadPage(0);
      setMode("book");
    } else {
      setMode("card");
      setWords([]);
    }
  };

  /* ---------------- DERIVED VALUE ---------------- */
  const hasMore = (page + 1) * PAGE_SIZE < total;

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
        padding: "20px",
      }}
    >
      <h1>📘 Technical Dictionary</h1>

      {/* CONTROLS */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px",
          justifyContent: "center",
          marginBottom: "20px",
          width: "100%",
          maxWidth: "600px",
        }}
      >
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search word..."
          style={{
            flex: "1",
            minWidth: "150px",
            padding: "8px",
          }}
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
      </div>

      {/* BOOK MODE */}
      {mode === "book" ? (
        <div style={{ width: "100%", maxWidth: "700px" }}>

          {/* A-Z GRID */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(30px, 1fr))",
              gap: "6px",
              marginBottom: "15px",
            }}
          >
            {alphabet.map((l) => (
              <button key={l} onClick={() => handleLetterClick(l)}>
                {l}
              </button>
            ))}

            <button onClick={handleAllClick}>All</button>
          </div>

          {/* WORDS */}
          {words.map((w, i) => (
            <BookItem key={i} word={w} darkMode={darkMode} />
          ))}

          {/* PAGINATION */}
          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "center",
              gap: "10px",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={() => {
                if (page === 0) return;
                const newPage = page - 1;

                activeLetter
                  ? loadLetterPage(activeLetter, newPage)
                  : loadPage(newPage);
              }}
              disabled={page === 0}
            >
              ⬅️ Prev
            </button>

            <span>
              Page {page + 1} / {Math.ceil(total / PAGE_SIZE)}
            </span>

            <button
              onClick={() => {
                if (!hasMore) return;
                const newPage = page + 1;

                activeLetter
                  ? loadLetterPage(activeLetter, newPage)
                  : loadPage(newPage);
              }}
              disabled={!hasMore}
            >
              Next ➡️
            </button>
          </div>
        </div>
      ) : (
        <div
          style={{
            border: "1px solid #333",
            padding: window.innerWidth < 500 ? "20px" : "40px",
            borderRadius: "12px",
            maxWidth: "500px",
            width: "100%",
            backgroundColor: darkMode ? "#222" : "#fff",
            textAlign: "center",
          }}
        >
          {!hasSearched || !currentWord ? (
            <p style={{ color: "#aaa" }}>
              📘 Search a word
            </p>
          ) : (
            <>
              <h2>{currentWord.word}</h2>

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
      )}
    </div>
  );
}

export default App;