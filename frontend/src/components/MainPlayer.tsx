import { Progress, Spin, Tabs } from "antd"

export function MainPlayer() {
  return (
    <div className="max-h-[800px] w-full min-w-[800px] overflow-auto border-x-[1px] border-b-[1px] border-gray-200 p-2 px-5">
      <Tabs
        animated
        defaultActiveKey="1"
        className="h-full w-full"
        items={[
          {
            key: "1",
            label: "Preview",
            children: (
              <>
                <Progress />
                <Spin tip="Loading" size="large">
                  <div className="content"> 正在加载中</div>
                </Spin>
              </>
            ),
          },
          {
            key: "2",
            label: "IPAdapter",
            children: <>IPAdapter</>,
          },
          {
            key: "3",
            label: "Controlnet",
            children: <>Controlnet</>,
          },
        ]}
      >
        ...
      </Tabs>
    </div>
  )
}
