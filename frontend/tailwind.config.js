/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "ai-bg": "#fef9c3",      // yellow tint for AI-generated content
        "ai-border": "#fbbf24",
        "human-bg": "#f0fdf4",   // green tint for human-authored content
        "human-border": "#4ade80",
      },
    },
  },
  plugins: [],
};
