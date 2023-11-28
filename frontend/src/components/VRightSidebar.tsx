import { useAnimateForm, useStore } from "../store"
import { Form, Input, InputNumber, Radio, Select, Tabs } from "antd"

import React, { useState } from "react"

interface FieldData {
  name: string | number | (string | number)[]
  value?: any
  touched?: boolean
  validating?: boolean
  errors?: string[]
}

interface CustomizedFormProps {
  onChange: (fields: FieldData[]) => void
  fields: FieldData[]
}

const CustomizedForm: React.FC<CustomizedFormProps> = ({ onChange, fields }) => {
  const { performances, aspect_ratios } = useStore()

  return (
    <Form
      layout="vertical"
      className="text-left"
      name="global_state"
      fields={fields}
      onFieldsChange={(_, allFields) => {
        onChange(allFields)
      }}
    >
      <Form.Item label="Performance" name="performance" tooltip="Use LCM for extreme speed">
        <Radio.Group>
          {performances.map((p) => (
            <Radio key={p} value={p}>
              {p}
            </Radio>
          ))}
        </Radio.Group>
      </Form.Item>
      <Form.Item label="Aspect Radios" name="aspect_ratio">
        <Radio.Group>
          {aspect_ratios.map((p) => (
            <Radio key={p} value={p}>
              {p}
            </Radio>
          ))}
        </Radio.Group>
      </Form.Item>
      <Form.Item label="Head Prompt" name="head prompt">
        <Input />
      </Form.Item>
      <Form.Item label="Tail Prompt" name="tail prompt">
        <Input />
      </Form.Item>
      <Form.Item label="Negative Prompt" name="negative prompt">
        <Input />
      </Form.Item>
      <Form.Item label="Seed" name="seed">
        <InputNumber />
      </Form.Item>
      <div className="flex space-x-5">
        <Form.Item label="Duration(s)" name="duration">
          <InputNumber />
        </Form.Item>
        <Form.Item label="FPS" name="fps">
          <InputNumber />
        </Form.Item>
      </div>
    </Form>
  )
}

export function VRightSidebar() {
  const { performances, motions, motion_loras, checkpoints, aspect_ratios, loras: loraOps } = useStore()
  const { loras, performance, aspect_ratio, setSettingsFormFields, settingsFormFields } = useAnimateForm()

  return (
    <div className="h-[800px] w-[300px] border-b-[1px] border-r-[1px] border-gray-200 px-5 py-2">
      <Tabs
        animated
        defaultActiveKey="1"
        className="h-full w-[260px]"
        items={[
          {
            key: "1",
            label: "Setting",
            children: (
              <CustomizedForm
                fields={settingsFormFields}
                onChange={(newFields) => {
                  setSettingsFormFields(newFields)
                }}
              />
            ),
          },
          {
            key: "2",
            label: "Models",
            children: (
              <Form
                layout="vertical"
                initialValues={{
                  checkpoint: "checkpoint",
                  motion: "motion",
                  motion_lora: "motion_lora",
                  loras: [
                    ["lora1", 1],
                    ["lora2", 1],
                    ["lora3", 1],
                    ["lora4", 1],
                    ["lora5", 1],
                  ],
                }}
                className="text-left"
              >
                <Form.Item label="Checkpoint" name="checkpoint">
                  <Select>
                    {checkpoints.map((p) => (
                      <Select.Option key={p.name} value={p.name}>
                        {p.name}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>
                {loras.map((lora, idx) => {
                  return (
                    <div className="flex space-x-5">
                      <Form.Item label={`Lora ${idx + 1}`} key={idx} name={["loras", idx, 0]}>
                        <Select
                          style={{
                            width: "150px",
                          }}
                        >
                          {loraOps.map((p) => (
                            <Select.Option key={p.name} value={p.name}>
                              {p.name}
                            </Select.Option>
                          ))}
                        </Select>
                      </Form.Item>
                      <Form.Item label="weight" name={["loras", idx, 1]}>
                        <InputNumber />
                      </Form.Item>
                    </div>
                  )
                })}
                <Form.Item label="Motion" name="motion">
                  <Select>
                    {motions.map((p) => (
                      <Select.Option value={p.name}>{p.name}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item label="Motion LoRA" name="motion_lora">
                  <Select>
                    {motion_loras.map((p) => (
                      <Select.Option value={p.name}>{p.name}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Form>
            ),
          },
          {
            key: "3",
            label: "Advanced",
            children: "Content of Tab Pane 3",
          },
        ]}
      ></Tabs>
    </div>
  )
}
