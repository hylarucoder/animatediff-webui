export default defineEventHandler(async (event) => {
    return {
        posts: [],
        postsByTag: {},
        tags: [],
    };
});
