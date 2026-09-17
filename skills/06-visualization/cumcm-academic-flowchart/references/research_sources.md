# 开发前研究来源与许可证边界

本实现只借鉴架构、布局、验证和错误处理思想，没有复制第三方项目代码。

| 来源 | 借鉴内容 | 许可证/边界 |
|---|---|---|
| OpenAI Codex Skill Creator | 精简入口、按需 references、脚本与验证 | 当前 Codex 内置规范 |
| Model Context Protocol Specification | 工具/资源分层、用户授权和数据边界 | 仅借鉴协议思想 |
| `jgraph/drawio-mcp` | draw.io 作为可编辑主文件、结构化工具返回与验证 | Apache-2.0；未复制代码 |
| `Agents365-ai/drawio-skill` | 自检迭代、布局走廊、可编辑输出 | 研究公开仓库并遵守其 LICENSE；未复制代码 |
| `Agents365-ai/mermaid-skill` | Mermaid 适合快速原型、复杂精确图转 draw.io | 未复制代码 |
| Graphviz 官方文档 | 分层布局、`rankdir`、spline/ortho 路由思想 | 仅借鉴算法接口思想 |
| Eclipse ELK 官方文档 | layered/radial/box/stress、overlap removal、compaction | 仅借鉴布局思想 |
| draw.io 官方 diagram generation 文档 | `mxGraphModel/mxCell/mxGeometry` 合法结构 | 仅实现公开文件格式 |
| W3C SVG 2 | `viewBox`、`text/tspan`、透明度和原生矢量结构 | 开放标准 |

竞赛模式不访问这些在线资源；所有核心实现与验证在本地完成。
