function UserDashboard({ onBack, onLogout = () => {}, darkMode }) {
  return (
  <div>
    <h1 style={{ color: darkMode ? "#fff" : "#111", textAlign: "center" }}>
      User Dashboard
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
      <button
        onClick={onBack}
        style={{
          background: darkMode ? "#333" : "#f2f2f2",
          color: darkMode ? "#fff" : "#111",
          border: darkMode ? "1px solid #555" : "1px solid #ddd",
          padding: "6px 12px",
          borderRadius: 6,
          cursor: "pointer",
        }}
      >
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

    
  </div>
);
}

export default UserDashboard;