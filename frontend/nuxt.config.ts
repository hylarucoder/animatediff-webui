import { defineNuxtConfig } from "nuxt/config"

function getGitCommitDateYMD() {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { execSync } = require("child_process")
  const date = execSync("git show -s --format=%ci HEAD").toString()
  return date.slice(0, 10).replaceAll("-", "")
}

export default defineNuxtConfig({
  srcDir: "src/",
  nitro: {
    routeRules: {
      "/": {
        isr: true,
      },
      "/posts/**": {
        // experimentalNoScripts: true,
      },
    },
    esbuild: {
      options: {
        target: "esnext",
      },
    },
  },
  css: ["~/assets/css/tailwind.css", "~/assets/scss/index.scss"],
  runtimeConfig: {
    public: {
      LATEST_COMMIT_DATE: getGitCommitDateYMD(),
      API_BASE_URL: process.env.NUXT_API_BASE_URL || "/api",
    },
  },
  modules: [
    "@nuxt/image",
    "@ant-design-vue/nuxt",
    "@nuxtjs/device",
    "@vueuse/nuxt",
    "@vueuse/motion/nuxt",
    "@pinia/nuxt",
    "@nuxt/content",
  ],
  antd: {
    // Options
  },
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },

  experimental: {
    typedPages: true,
    componentIslands: true,
    typescriptBundlerResolution: true,
  },

  app: {
    head: {
      htmlAttrs: {
        lang: "en",
      },
      viewport: "width=device-width,initial-scale=1",
      link: [
        {
          rel: "icon",
          href: "/favicon.ico",
          sizes: "any",
        },
        {
          rel: "icon",
          type: "image/svg+xml",
          href: "/nuxt.svg",
        },
        {
          rel: "apple-touch-icon",
          href: "/apple-touch-icon.png",
        },
      ],
      script: [],
      meta: [
        {
          name: "charset",
          content: "utf-8",
        },
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1, maximum-scale=5",
        },
        {
          name: "apple-mobile-web-app-status-bar-style",
          content: "black-translucent",
        },
      ],
    },
  },
  googleFonts: {
    families: {
      Inter: true,
    },
  },

  devtools: {
    enabled: true,
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          experimentalMinChunkSize: 500_000,
          inlineDynamicImports: true,
        },
      },
    },
  },
  ssr: false,
})
