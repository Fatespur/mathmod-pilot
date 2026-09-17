# draw.io XML 输出

使用未压缩的：

`mxfile → diagram → mxGraphModel → root → mxCell`

- `id=0` 为根，`id=1` 为默认图层。
- 节点为 `vertex=1`，边为 `edge=1` 并引用稳定 `source/target`。
- 几何信息放入 `mxGeometry`；边拐点放入 `Array as="points"`。
- 所有文本和属性由 XML 库转义，支持 `& < > " ' `。
- 不记录本地绝对路径、身份信息或远程资源。
- `.drawio` 必须可由 diagrams.net 直接打开并继续编辑。

官方参考：draw.io 的 AI diagram generation 和 XML export 文档。实现仅借鉴格式，不复制第三方代码。
