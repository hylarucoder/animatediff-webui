export enum TStatus {
    PENDING = "PENDING",
    LOADING = "LOADING",
    SUCCESS = "SUCCESS",
    ERROR = "ERROR",
}

const video_url = ref("")
const status = ref(TStatus.PENDING)
const videoRef = ref<HTMLVideoElement | null>(null)

export const usePlayer = () => {
    return {
        status,
        video_url,
        videoRef,
        reloadVideo: () => {
            console.log(videoRef, videoRef?.value)
            videoRef?.value?.load()
        },
    }
}
