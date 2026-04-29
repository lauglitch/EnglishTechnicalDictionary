// src/api/api.js

import axios from "axios";
import { supabase } from "../lib/supabase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL + "/words",
});

/* ---------------- REQUEST INTERCEPTOR ---------------- */
api.interceptors.request.use(async (config) => {
  // get session once (cached internally by Supabase)
  const { data } = await supabase.auth.getSession();

  const token = data?.session?.access_token;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    console.warn("No Supabase session found for request");
  }

  return config;
});

/* ----------------  401s ---------------- */
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      console.warn("401 Unauthorized → token/session issue");
    }
    return Promise.reject(err);
  },
);

export default api;
