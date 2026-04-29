import { useEffect } from "react";
import { supabase } from "../lib/supabase";

const SESSION_DURATION = 60 * 60 * 1000; // 1 hour

export default function SessionManager() {
  useEffect(() => {
    const interval = setInterval(async () => {
      const loginTime = localStorage.getItem("login_time");

      if (!loginTime) return;

      const expired = Date.now() - loginTime > SESSION_DURATION;

      if (expired) {
        await supabase.auth.signOut();
        localStorage.removeItem("login_time");
        window.location.href = "/login";
      }
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  return null;
}