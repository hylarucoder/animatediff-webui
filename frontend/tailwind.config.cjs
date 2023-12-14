const { fontFamily } = require("tailwindcss/defaultTheme")
const {
  iconsPlugin,
  getIconCollections,
} = require("@egoist/tailwindcss-icons")

/** @type {import("tailwindcss").Config} */
module.exports = {
  // darkMode: ["class"],
  content: [
    "./src/**/*.{vue,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter var", ...fontFamily.sans],
      },
    },
  },
  plugins: [
    // require("@tailwindcss/typography"),
    // require("tailwindcss-animate"),
    iconsPlugin({
      // Select the icon collections you want to use
      // You can also ignore this option to automatically discover all icon collections you have installed
      collections: getIconCollections(["mdi", "lucide", "tabler", "carbon"]),
    }),
  ],
  corePlugins: {
    preflight: false,
  }
}
