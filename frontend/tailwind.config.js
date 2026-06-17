/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bordo: {
          DEFAULT: '#580F1C',
          50: '#fdf2f4',
          100: '#f9e2e6',
          200: '#f0c4cc',
          300: '#e095a3',
          400: '#c95d72',
          500: '#a8324a',
          600: '#8a1f35',
          700: '#6b1529',
          800: '#580F1C',
          900: '#480F18',
          950: '#2a090f',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '2px',
        sm: '2px',
        md: '2px',
        lg: '2px',
      },
      boxShadow: {
        none: 'none',
      },
    },
  },
  plugins: [],
};
