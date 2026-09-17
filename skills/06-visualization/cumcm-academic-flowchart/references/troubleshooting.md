# 故障排查

## XML 无法打开

检查 XML 是否完整、特殊字符是否转义、节点 ID 是否唯一、边引用是否存在、`mxGeometry` 是否有 `as="geometry"`。

## 节点或文字裁切

缩短 `short_label`、增加节点高度、扩大画布或拆图；禁止继续缩小字体。

## 箭头穿节点

检查是否使用多端口逃逸段和障碍走廊路由；禁止只在水平优先/垂直优先两种中点折线中二选一。必要时增加 corridor 偏移、提高间距或换用另一布局。

## 框架图退化为一条步骤线

检查 ModelingIR 是否包含 `framework_role/stage/module/branch/parent_id`，以及原文中的具体方法名是否被保留。至少建立一个主方法、三个子方法/组件、四层语义深度和真实的分支—汇聚关系；多小问优先选择 `question_architecture`，让每一问内部形成独立的方法结构，再选择 `method_framework`、`hierarchical_tree`、`layered_architecture`、双流、中心模型或闭环布局。禁止仅把同一条链弯成蛇形、U 形或回字形，也禁止直接绕过 ModelingIR 拼装最终图。

## PNG 不透明或尺寸不足

确认 `--transparent`、图像模式 RGBA、alpha 极值包含小于 255 的值，长边达到配置，DPI 元数据存在。

## 中文乱码

检查字体探测报告。Windows 优先 Microsoft YaHei/SimHei；缺失时安装 Noto/Source Han CJK，不把字体文件提交到 Skill。

## 可选依赖缺失

纯文本、JSON、源码、draw.io 和 SVG 核心流程仍可运行。PDF/DOCX/XLSX/PNG 分别提示 pypdf/python-docx/openpyxl/Pillow。不得伪造产物。

## 质量分不足

查看 `quality_report.json`，按阻断项优先修复。最多三轮自动修正后仍失败，应交付可验证产物与准确未解决清单，而不是宣称通过。
