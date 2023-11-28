import { useAnimateForm, useStore } from "../store"
import { Button, Form, Input, InputNumber, Radio, Select } from "antd"
import React from "react"

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
  const { presets, projects } = useStore()
  const { setPreset } = useAnimateForm()

  return (
    <Form
      layout="inline"
      fields={fields}
      onFieldsChange={(_, allFields) => {
        onChange(allFields)
      }}
      className="text-left"
    >
      <Form.Item
        label="Preset"
        style={{
          width: "300px",
        }}
      >
        <Select
          onChange={(value) => {
            const preset = presets.find((p) => p.name === value)
            if (!preset) {
              return
            }
            console.log("preset", preset)
            setPreset(preset)
          }}
          options={presets.map((p) => ({ label: p.name, value: p.name }))}
        />
      </Form.Item>
      <Form.Item label="Project">
        <Select
          style={{
            width: "200px",
          }}
          options={projects.map((p) => ({ label: p, value: p }))}
        />
      </Form.Item>
    </Form>
  )
}

export function TopNav() {
  const loading = false
  const { presets, projects, checkpoints, loras } = useStore()
  const { setPreset, setTopbarFormFields, topbarFormFields } = useAnimateForm()

  return (
    <div className="flex w-full justify-evenly border-[1px] px-5 text-center">
      <div className="form-item-no-feedback flex flex-1 space-x-3 py-2 align-middle">
        <CustomizedForm
          fields={topbarFormFields}
          onChange={(newFields) => {
            setTopbarFormFields(newFields)
            console.log("newFields", newFields)
          }}
        />
      </div>

      <div className="flex items-center justify-center space-x-3">
        <Button
          loading={loading}
          onClick={() => {
            console.log("onClick")
          }}
        >
          Generate
        </Button>
        <Button
          onClick={() => {
            console.log("load video")
          }}
        >
          load video
        </Button>
      </div>
    </div>
  )
}
