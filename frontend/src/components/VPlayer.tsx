import { formatProxyMedia } from "~/client"
import { AButton, APopover, ASlider, ASpin } from "#components"

export default defineComponent({
  setup() {
    const optionsStore = useOptionsStore()
    const { optAspectRadios } = optionsStore
    const formStore = useFormStore()
    const { aspectRatio, cameraControl } = storeToRefs(formStore)

    const videoPlayerStore = useVideoPlayer()
    const { videoRef, waiting, src, currentTime, playing, duration } = storeToRefs(videoPlayerStore)
    const { loadVideo, play, pause, toggle } = videoPlayerStore
    const videoExportStore = useVideoExportStore()
    const { task } = storeToRefs(videoExportStore)

    onMounted(() => {
      const srcValue = formatProxyMedia(
        "C:\\AIGC\\App\\animatediff-webui\\projects\\001-demo\\draft\\2023-12-07T13-52-47\\video.mp4",
      )
      loadVideo(srcValue)
    })

    const downloadUrl = () => {
      const url = src.value
      window.open(url, "_blank")
    }

    const size = computed(() => {
      const a = {
        "16:9": "768x432",
        "4:3": "768x576",
        "1:1": "600x600",
        "3:4": "576x768",
        "9:16": "432x768",
      }[aspectRatio.value].split("x")
      return {
        width: a[0],
        height: a[1],
      }
    })

    const togglePlaying = () => {
      playing.value = !playing.value
    }

    // The rest of your component logic...

    return () => (
      <div class="relative flex h-full w-full flex-col overflow-hidden">
        <div class="flex items-center justify-center">
          <div v-show={task.value.status === TStatus.PENDING}>
            <div
              class="bg-amber-50"
              style={{
                width: size.value.width + "px",
                height: size.value.height + "px",
              }}
            >
              {aspectRatio}
            </div>
          </div>
          <div v-show={task.value.status === TStatus.ERROR}>error</div>
          <ASpin v-show={task.value.status === TStatus.RUNNING}> generating video</ASpin>
          <div v-show={task.value.status === TStatus.SUCCESS}>
            <video ref={videoRef} id="video" crossorigin="anonymous" class="max-h-[600px] w-full" />
          </div>
        </div>

        <div class="space-between absolute bottom-0 left-0 h-[--player-bar-height] w-full border-t-[1px] border-zinc-100 bg-white py-1 pl-5 pr-1">
          <div class="flex justify-between">
            <div class="flex space-x-2 font-mono text-zinc-600">
              <span class="leading-8">{formatDurationHHMMSS(currentTime.value)}</span>
              <span class="leading-8"> / </span>
              <span class="leading-8">{formatDurationHHMMSS(duration.value)}</span>
            </div>
            <div>
              <AButton
                onClick={() => {
                  playing.value = !playing.value
                }}
                class="flex items-center justify-center"
              >
                {playing.value ? (
                  <span class="i-lucide-pause h-4 w-4 text-zinc-600" />
                ) : (
                  <span class="i-lucide-play h-4 w-4 text-zinc-600" />
                )}
              </AButton>
            </div>
            <div class="flex space-x-2">
              <AButton
                onClick={() => {
                  toggle()
                }}
                class="flex items-center justify-center"
              >
                <span class="i-lucide-fullscreen h-4 w-4 text-zinc-600" />
              </AButton>
              <AButton
                onClick={() => {
                  downloadUrl()
                }}
                class="flex items-center justify-center"
              >
                <span class="i-lucide-download h-4 w-4 text-zinc-600" />
              </AButton>
              <APopover placement="topLeft">
                {{
                  content: () => (
                    <div class="max-w-[180px]">
                      <h4 class="text-md my-1">Aspect Ratio</h4>
                      <a-radio-group v-model:value={aspectRatio.value}>
                        {optAspectRadios.map((ar) => (
                          <a-radio key="ar.value" class="font-mono text-zinc-800" value="ar.value" label="ar.label">
                            {ar.value}
                          </a-radio>
                        ))}
                      </a-radio-group>
                    </div>
                  ),
                  default: () => <AButton class="w-[60px] text-zinc-600">{aspectRatio.value}</AButton>,
                }}
              </APopover>
              <APopover placement="topLeft">
                {{
                  default: () => (
                    <AButton class="flex items-center justify-center text-zinc-600">
                      <span class="i-lucide-switch-camera h-4 w-4 text-zinc-600"></span>
                    </AButton>
                  ),
                  content: () => (
                    <div class="max-w-[300px]">
                      <h4 class="text-md my-1">Camera Control</h4>
                      <div class="mt-1 flex justify-between space-x-3">
                        <v-camera-control-item layout="left" icon="i-lucide-arrow-left">
                          <ASlider
                            style="width: 100px"
                            v-model:value={cameraControl.value.panLeft}
                            min="0"
                            max="1"
                            step="0.1"
                            reverse
                          />
                        </v-camera-control-item>
                        <v-camera-control-item layout="right" icon="i-lucide-arrow-right">
                          <ASlider
                            style="width: 100px"
                            v-model:value={cameraControl.value.panRight}
                            min="0"
                            max="1"
                            step="0.1"
                          />
                        </v-camera-control-item>
                      </div>

                      {/* <div class="flex justify-between space-x-3"> */}
                      {/*   <v-camera-control-item layout="left" icon="i-lucide-arrow-down"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.tileDown" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*       reverse */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/*   <v-camera-control-item layout="right" icon="i-lucide-arrow-up"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.tileUp" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/* </div> */}
                      {/* <div class="flex justify-between space-x-3"> */}
                      {/*   <v-camera-control-item layout="left" icon="i-lucide-rotate-ccw"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.rollingClockwise" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*       reverse */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/*   <v-camera-control-item layout="right" icon="i-lucide-rotate-cw"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.rollingAnticlockwise" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/* </div> */}
                      {/* <div class="flex justify-between space-x-3"> */}
                      {/*   <v-camera-control-item layout="left" icon="i-lucide-zoom-in"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.zoomIn" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*       reverse */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/*   <v-camera-control-item layout="right" icon="i-lucide-zoom-out"> */}
                      {/*     <a-slider */}
                      {/*       style="width: 100px" */}
                      {/*       v-model:value="cameraControl.zoomOut" */}
                      {/*       min="0" */}
                      {/*       max="1" */}
                      {/*       step="0.1" */}
                      {/*     /> */}
                      {/*   </v-camera-control-item> */}
                      {/* </div> */}
                    </div>
                  ),
                }}
              </APopover>
            </div>
          </div>
        </div>
      </div>
    )
  },
})
