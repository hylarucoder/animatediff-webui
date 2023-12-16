// import * as zhCN from "~/locales/zh_CN"
// import * as en from "~/locales/en"
//
// const locales = {
//   zh_CN: zhCN,
//   en,
// }
//
// const locale = ref("en")
//
// export const useI18n = () => {
//   const translate = (key) => {
//     const parts = key.split(".")
//     let translation = locales[locale.value].default
//     for (const part of parts) {
//       if (translation[part] !== undefined) {
//         translation = translation[part]
//       } else {
//         return key // return original key if no translation available
//       }
//     }
//     return translation.trim()
//   }
//
//   const t = (key, _) => {
//     return computed(() => translate(key))
//   }
//
//   const setLocale = (newLocale) => {
//     locale.value = newLocale
//   }
//
//   return { t, locale, setLocale }
// }
//
// export const useTrans = () => {
//   const { t, locale, setLocale } = useI18n()
//   return {
//     t,
//     locale,
//     setLocale,
//   }
// }
