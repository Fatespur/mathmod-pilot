# PNG 渲染

PNG 是兼容格式。默认透明背景、300 DPI、长边 4800 px，最低 3200 px；支持 600 DPI 和 6400 px。

渲染优先思想为 `resvg → CairoSVG → headless Chromium → ImageMagick`。本 Skill 的稳定离线实现使用 Pillow 直接按同一 Scene Graph 在目标像素上栅格化，属于矢量场景高质量直接渲染：

- 不使用系统截图；
- 不先生成低分辨率再放大；
- RGBA 透明通道；
- 抗锯齿形状和清晰中文字体；
- DPI 元数据与像素尺寸同时验证。

Pillow 不可用时，draw.io 和 SVG 仍可生成，但必须返回准确依赖错误，不得伪造或输出空白 PNG。
