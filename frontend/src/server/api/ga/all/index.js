import { getAllValues } from "~/utils/ga";
export default defineEventHandler(async () => {
    return await getAllValues();
});
