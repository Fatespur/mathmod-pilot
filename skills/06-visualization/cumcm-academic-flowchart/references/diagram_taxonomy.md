# 图表类型路由

支持以下 `diagram_type`：

| 类型 | 用途 |
|---|---|
| `overall_route` | 整篇论文的多问题方法框架与依赖 |
| `question_flow` | 单一小问的主方法—子方法框架 |
| `question_dependency` | 多小问数据、参数和模型依赖 |
| `data_pipeline` | 数据读取、清洗、特征与输出 |
| `optimization_flow` | 目标、变量、约束、求解与检验 |
| `prediction_flow` | 划分、训练、预测、残差与泛化 |
| `evaluation_flow` | 指标、权重、评价、排序与敏感性 |
| `statistical_analysis_flow` | 假设、统计量、显著性与区间 |
| `mechanism_model` | 系统边界、变量、方程与仿真 |
| `algorithm_flow` | 判断、循环与终止条件 |
| `model_architecture` | 分层模型或神经网络结构 |
| `training_inference_flow` | 训练流和推理流 |
| `validation_flow` | 诊断、交叉验证和不确定性 |
| `multi_model_fusion` | 多模型并行与融合 |
| `sensitivity_analysis_flow` | 参数扰动、响应与结论 |

总体图不得塞入所有算法细节，但必须保留各小问的主方法、关键子方法和依赖。复杂单问和模型检验应单独拆图；除短小且严格时序的算法流外，不得把框架图退化为线性步骤图。
