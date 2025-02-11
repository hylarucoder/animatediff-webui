# AnimateDiff WebUI

> Improved from [animatediff-cli-prompt-travel](https://github.com/s9roll7/animatediff-cli-prompt-travel) , simplified some parameters and workflows, provided some UI and the workflow I commonly use.

## Features

- [ ] Project like structure, you just copy a project folder and do all workflows in that folder!!
- [ ] webui && yaml syntax
- [ ] Windows && Linux, mac with limit support (mps is hard)

## Installation

```bash
git clone https://github.com/hylarucoder/animatediff-webui
cd animatediff-webui
py3.10 -m venv venv
# linux/macOS
source venv/bin/activate
# windows
venv\Scripts\activate.bat
pip install pdm 
pdm install
# linux/windows
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -m pip install onnxruntime-gpu xformers
# macos
python -m pip install torch torchvision torchaudio 
python -m pip install onnxruntime-silicon

# window
pip install segment-anything-hq groundingdino-py gitpython "rembg[gpu]"
```

## Credit

> I did very little, the code is mainly based on the following projects.

- [guoyww/AnimateDiff](https://github.com/guoyww/AnimateDiff)
- [animatediff-cli-prompt-travel](https://github.com/s9roll7/animatediff-cli-prompt-travel)

