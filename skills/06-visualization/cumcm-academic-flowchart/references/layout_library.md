# 布局库

## 索引

- 布局家族
- 专用路由

| 家族 | 布局名称 | 适用语义 |
|---|---|---|
| 线性 | `left_to_right/right_to_left/top_to_bottom/bottom_to_top` | 简单时序、训练、推理 |
| 双流 | `dual_stream/parallel_lanes/split_merge` | 多源数据、双模型、组合权重 |
| 泳道 | `horizontal_swimlane/vertical_swimlane/question_swimlane` | 多小问、角色或阶段 |
| 汇聚发散 | `fan_in/fan_out/y_shape/hourglass` | 多源融合、集成、多结果 |
| 中心辐射 | `hub_spoke/radial/central_model` | 共享核心模型或核心数据 |
| 环形迭代 | `circular_cycle/feedback_ring/iterative_loop` | 训练、校准、优化、控制反馈 |
| 回字形 | `rectangular_loop/hui_shape/perimeter_flow` | 建模—求解—检验—改进闭环 |
| U 形 | `u_shaped/horseshoe` | 左侧建模、底部求解、右侧评价 |
| 蛇形 | `serpentine/s_curve/zigzag` | 阶段多、版面接近方形 |
| 同心 | `concentric/nested_layers/core_shell` | 系统边界、内外层变量 |
| 矩阵 | `matrix/quadrant/grid_dependency` | 数据×模型、问题×方法、多方法比较 |
| 分层架构 | `layered_architecture/modular_architecture/encoder_fusion_decoder` | 神经网络、多模态和模块化系统 |
| 方法框架 | `method_framework/modular_method_map` | 主方法、子方法、输入、求解、验证的横向模块架构 |
| 层级方法树 | `hierarchical_tree/method_tree` | 自上而下的方法分解、并行检验与结果汇聚 |

回字形、环形和 U 形必须采用专用节点位置和正交/闭环路由；不得用简单直线穿过中心。蛇形保持明确阅读顺序，不能为了紧凑破坏逻辑。

默认优先方法框架或层级方法树。节点不少于 6 个且存在主/子方法时，禁止选择纯线性布局作为主方案；线性布局只服务于不可分支的短时序。
