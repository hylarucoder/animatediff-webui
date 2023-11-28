import { getArticleViews, setArticleViews } from "~/utils/ga";
export default defineEventHandler(async (event) => {
    const body = await getQuery(event);
    const path = body.path || "/";
    let count = await getArticleViews(path, 1);
    await setArticleViews(path, ++count);
    return {
        path: "/",
        views: count,
    };
});
