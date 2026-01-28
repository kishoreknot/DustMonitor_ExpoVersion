/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./frontend/*.html",        // Finds home.html and admin.html
    "./frontend/js/**/*.js",    // Finds all JS files in subfolders
    "./frontend/js/*.js",    // Finds all JS files in subfolders
    "./*.py"                    // OPTIONAL: If you generate HTML/classes inside Python
  ],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [],
}