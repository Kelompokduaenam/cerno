import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Arsitektur CERNO §3.5: web & API satu origin, API di /api/v1/...
// Saat dev, proxy ke FastAPI agar frontend memanggil path relatif (tanpa CORS).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: false },
    },
  },
});
