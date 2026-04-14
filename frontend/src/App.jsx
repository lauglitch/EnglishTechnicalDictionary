import { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000/words";

function App() {
  const [words, setWords] = useState([]);
  const [index, setIndex] = useState(0);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function loadWords() {
      try {
        const res = await axios.get(`${API}?skip=0&limit=50`);
        setWords(res.data);
        setIndex(0);
      } catch (err) {
        console.error("Error loading words:", err);
      }
    }

    loadWords();
  }, []);

  const handleSearch = async () => {
    console.log("SEARCH URL:", `${API}/${search}`);
    try {
      if (!search) {
        const res = await axios.get(`${API}?skip=0&limit=50`);
        setWords(res.data);
        setIndex(0);
        return;
      }

      const res = await axios.get(`${API}/${search}`);
      setWords([res.data]);
      setIndex(0);
    } catch (err) {
      console.log("STATUS:", err.response?.status);
      console.log("DATA:", err.response?.data);
      console.log("FULL ERROR:", err);

      alert("Word not found");
    }
   
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Dictionary</h1>

      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search word..."
      />
      <button onClick={handleSearch}>Search</button>

      {words.length > 0 ? (
        <>
          <h2>{words[index].word}</h2>
          <p>{words[index].definition}</p>
          <p><strong>Grammar:</strong> {words[index].grammar_class || "-"}</p>
          <p><strong>Topic:</strong> {words[index].topic || "-"}</p>
          <p><strong>Example:</strong> {words[index].example || "-"}</p>
          <p><strong>Author:</strong> {words[index].author}</p>
          <p><strong>Status:</strong> {words[index].status}</p>
        </>
      ) : (
        <p>No words to display</p>
      )}
    </div>
  );
}

export default App;