import { useEffect, useState } from "react"
import "./App.css"
import { useAnimateForm, useStore } from "./store"
import { urlPrefix } from "./consts.ts"
import { TopNav } from "./components/TopNav.tsx"
import { VRightSidebar } from "./components/VRightSidebar.tsx"
import { MainPlayer } from "./components/MainPlayer.tsx"
import { Spin } from "antd"

function Main() {
  return (
    <div className="w-full p-0 px-8">
      <TopNav />
      <div className="border-x-1 border-b-1 flex justify-between">
        <MainPlayer />
        <VRightSidebar />
      </div>
    </div>
  )
}

function App() {
  const [loading, setLoading] = useState(true)
  const { setOptions } = useStore()
  const { setPreset, setTopbarFormFields } = useAnimateForm()
  useEffect(() => {
    fetch(urlPrefix + "/api/options", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setOptions(data)
        const preset_name = data.presets[0].name
        const preset = data.presets.find((p) => p.name === preset_name)
        if (!preset) {
          return
        }
        setPreset(preset)
        setTopbarFormFields([
          {
            name: "preset",
            value: preset_name,
          },
          {
            name: "project",
            value: data.projects[0],
          },
        ])
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])
  return <>{loading ? <Spin /> : <Main />}</>
}

export default App
