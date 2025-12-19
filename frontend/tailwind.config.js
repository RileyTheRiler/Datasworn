/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        disco: {
          bg: "#101014",       // Darker charcoal, almost black
          paper: "#beb8a8",    // More muted, dirty paper
          accent: "#d45d35",   // Rust orange (Reference: Jacket)
          cyan: "#6be4e3",     // Pale cyan (Reference: Skill text)
          purple: "#7d6fb8",   // Muted Psyche
          red: "#b93f3f",      // Muted Physique
          blue: "#4a7a96",     // Slate blue (Reference: UI panels)
          yellow: "#e0ae42",   // Dull gold
          muted: "#5a5a6a",
          panel: "rgba(22, 25, 30, 0.95)", // Dark slate panel
          dark: "#0b0c0f",
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        hand: ['"Caveat"', 'cursive'],
      },
      backgroundImage: {
        'grunge': "linear-gradient(rgba(16, 16, 20, 0.95), rgba(16, 16, 20, 0.85)), url('/assets/textures/grunge_paper.png')", // Darker overlay
        'noise': "url('/assets/textures/noise.png')",
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px rgba(0,0,0,0.5)',
        'glow': '0 0 10px rgba(107, 228, 227, 0.3)',
      }
    },
  },
  plugins: [],
}
