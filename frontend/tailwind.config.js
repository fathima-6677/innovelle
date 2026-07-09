/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aws: {
          navy: 'var(--aws-navy)',
          dark: 'var(--aws-dark)',
          orange: 'var(--aws-orange)',
          teal: 'var(--aws-teal)',
          blue: 'var(--aws-blue)',
          gray: 'var(--aws-gray)',
          slate: 'var(--aws-slate)',
          border: 'var(--aws-border)',
        }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
