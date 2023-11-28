import { BetaAnalyticsDataClient } from "@google-analytics/data"

export const getArticleViews = async (path, value = 1) => {
  const cache = useStorage()
  return (await cache.getItem(`ga:${path}`)) || value
}

export const setArticleViews = async (path, count) => {
  const cache = useStorage()
  await cache.setItem(`ga:${path}`, count)
}

export const getAllValues = async () => {
  await getGAViewsFromCache()
  const cache = useStorage()
  const allKeys = await cache.getItem("ga:allKeys")
  const res = []
  for (const k of allKeys || []) {
    const v = await getArticleViews(k)
    res.push({
      path: k,
      views: v,
    })
  }
  return res
}

const client = new BetaAnalyticsDataClient({
  keyFilename: "./ga-simpleaiart.json",
})

export async function getGAViewsFromCache() {
  const cache = useStorage()
  const gaCached = await cache.getItem("ga:cached")
  if (gaCached) {
    return
  }
  const allKeys = []
  try {
    const response = await client.runReport({
      property: "properties/403171386",
      dateRanges: [{ startDate: "2010-01-01", endDate: "yesterday" }],
      dimensions: [
        {
          name: "pagePath",
        },
      ],
      metrics: [
        {
          name: "screenPageViews",
        },
      ],
      metricAggregations: ["TOTAL"],
      limit: "100",
    })
    const rows = response[0].rows
    for (const row of rows) {
      const path = row.dimensionValues[0].value
      const views = parseInt(row.metricValues[0].value)
      await setArticleViews(path, views)
      allKeys.push(path)
    }
  } catch (e) {
    console.log(e)
  } finally {
    await cache.setItem("ga:cached", true)
    await cache.setItem("ga:allKeys", allKeys)
  }
}
