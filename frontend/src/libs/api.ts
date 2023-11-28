export const getPageTable = async (pageId: string, apiUrl = "https://api.vue-notion.workers.dev/v1"): Promise<any[]> =>
  await $fetch(`${apiUrl}/table/${pageId}`)

export const getPageBlocks = async (pageId: string, apiUrl = "https://api.vue-notion.workers.dev/v1") =>
  await $fetch(`${apiUrl}/page/${pageId}`)
