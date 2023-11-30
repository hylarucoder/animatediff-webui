import { TLocale } from "./en"

const cn: TLocale = {
  WIP: "该功能仍在开发中……",
  Home: {
    Title: "我是谁?\n海拉鲁编程客",
    Subtitle: `\
Hey! 我是一名独立开发者兼视频博主, 
专注"前端"、"后端"和"AIGC",
希望我的产品和代码能够影响成千上万的人。\
`,
  },
  Articles: {
    Title: "Stable Diffusion: All I Know about",
    Subtitle: `有关编程、AIGC、产品设计及其他的长篇思考或者笔记。`,
  },
  Error: {
    Unauthorized:
      "访问密码不正确或为空，请前往 [登录](/#/auth) 页输入正确的访问密码，或者在 [设置](/#/settings) 页填入你自己的 OpenAI API Key。",
  },
  Auth: {
    Title: "需要密码",
    Tips: "管理员开启了密码验证，请在下方填入访问码",
    Input: "在此处填写访问码",
    Confirm: "确认",
    Later: "稍后再说",
  },
  ChatItem: {
    ChatItemCount: `{count} 条对话`,
  },
}

export default cn
