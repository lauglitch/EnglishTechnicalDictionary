import axios from "axios";

const api = axios.create({
  baseURL: "https://englishtechnicaldictionary.onrender.com",
});

// Automatically attach admin email
api.interceptors.request.use((config) => {
  const email = localStorage.getItem("adminEmail");

  if (email) {
    config.headers["x-user-email"] = email;
  }

  return config;
});

export default api;
