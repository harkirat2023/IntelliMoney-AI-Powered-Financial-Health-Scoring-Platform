/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        display: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        cyber: {
          black: "#020204",
          cyan: "#00f5ff",
          pink: "#ff007f",
          purple: "#1f1035",
          "purple-light": "#2d1b4e",
          "cyan-dim": "rgba(0,245,255,0.15)",
          "pink-dim": "rgba(255,0,127,0.15)",
        },
        brand: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
        },
        accent: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        neutral: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
          950: "#020617",
        },
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "float-slow": "float 8s ease-in-out infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "pulse-neon-cyan": "pulse-neon-cyan 2s ease-in-out infinite",
        "pulse-neon-pink": "pulse-neon-pink 2s ease-in-out infinite",
        "gradient-shift": "gradient-shift 8s ease infinite",
        "slide-up": "slide-up 0.5s ease-out",
        "fade-in": "fade-in 0.5s ease-out",
        "mesh-drift": "mesh-drift 20s ease-in-out infinite",
        "border-glow": "border-glow 3s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(16, 185, 129, 0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(16, 185, 129, 0.6)" },
        },
        "pulse-neon-cyan": {
          "0%, 100%": { boxShadow: "0 0 15px rgba(0,245,255,0.2)" },
          "50%": { boxShadow: "0 0 30px rgba(0,245,255,0.5)" },
        },
        "pulse-neon-pink": {
          "0%, 100%": { boxShadow: "0 0 15px rgba(255,0,127,0.2)" },
          "50%": { boxShadow: "0 0 30px rgba(255,0,127,0.5)" },
        },
        "gradient-shift": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "slide-up": {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "mesh-drift": {
          "0%, 100%": { transform: "translate(0,0) rotate(0deg)" },
          "25%": { transform: "translate(5%,5%) rotate(1deg)" },
          "50%": { transform: "translate(-3%,2%) rotate(-0.5deg)" },
          "75%": { transform: "translate(2%,-3%) rotate(0.5deg)" },
        },
        "border-glow": {
          "0%, 100%": { borderColor: "rgba(0,245,255,0.2)" },
          "50%": { borderColor: "rgba(0,245,255,0.5)" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "mesh-cyan": "radial-gradient(circle at 20% 30%, rgba(0,245,255,0.03) 0%, transparent 50%)",
        "mesh-magenta": "radial-gradient(circle at 80% 70%, rgba(255,0,127,0.03) 0%, transparent 50%)",
      },
    },
  },
  plugins: [],
};
