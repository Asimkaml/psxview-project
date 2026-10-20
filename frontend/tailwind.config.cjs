/**** Tailwind config for PSXviewAI ****/

/​** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0B4F3F", // dark green accent
          light: "#0F766E",
        },
        muted: {
          DEFAULT: "#6B7280", // gray text
        },
      },
      borderRadius: {
        card: "0.75rem",
      },
    },
  },
  plugins: [],
};
