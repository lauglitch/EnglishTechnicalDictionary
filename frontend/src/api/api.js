import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL + "/words",
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
