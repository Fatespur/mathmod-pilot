# 中英文论文短语库

## 内容索引

  - English Academic Phrase Bank
    - Summary Phrases
    - Introduction Phrases
    - Model Description Phrases
    - Results Phrases
    - Sensitivity Analysis Phrases
    - Conclusion Phrases
  - CUMCM Chinese Academic Phrase Bank (国赛中文短语库)
    - 摘要短语
    - 问题重述短语
    - 模型建立短语
    - 模型求解短语
    - 结果分析短语
    - 模型检验短语
    - 灵敏度分析短语
    - 模型评价短语
    - 结论短语（CRITICAL：禁止分点）
    - 学术表述模板

## English Academic Phrase Bank

### Summary Phrases
```
- "This paper presents a comprehensive approach to..."
- "We develop a [type] model that [what it does]"
- "The model achieves [metric] of [value], demonstrating [conclusion]"
- "Sensitivity analysis confirms the robustness of our approach"
- "Our results indicate that [key finding]"
```

### Introduction Phrases
```
- "The [problem] has significant implications for [field/application]"
- "Recent advances in [field] have highlighted the importance of..."
- "Previous studies have addressed this problem using [methods], but..."
- "This paper proposes a novel [approach/framework] to address..."
```

### Model Description Phrases
```
- "We formulate the problem as a [linear programming / differential equation / ...]"
- "The objective function is defined as..."
- "Subject to the following constraints:"
- "The model is solved using [algorithm], implemented in [language/tool]"
- "The optimization converges to [value] after [N] iterations"
```

### Results Phrases
```
- "The results demonstrate that..."
- "As shown in Figure [N], the [variable] exhibits [pattern]"
- "Table [N] presents the comparison between..."
- "The model achieves an accuracy of [value] on the test set"
- "The 95% confidence interval is [lower, upper]"
```

### Sensitivity Analysis Phrases
```
- "Sobol global sensitivity analysis indicates that..."
- "Parameter [X] contributes [S1] of the total variance"
- "The Morris screening method identifies [X] and [Y] as the most influential parameters"
- "The model is most sensitive to changes in [parameter], with..."
- "These results confirm the robustness of our model"
```

### Conclusion Phrases
```
- "In conclusion, this paper has developed..."
- "Our approach successfully addresses the [problem]"
- "The key contributions of this work are:"
- "Future work could extend this approach by..."
```

## CUMCM Chinese Academic Phrase Bank (国赛中文短语库)

国赛模式仅参考本节的中文表达，不得混入英文竞赛模板。以下短语是可改写的表达素材，不是必须逐字使用的模板；优先根据证据写出自然、具体的句子，避免整篇呈现机械套话。

### 摘要短语
```
- "本文针对...问题，建立了...模型，实现了..."
- "首先，...；其次，...；最后，..."
- "结果表明，...，具有...的精度"
- "模型的R² = 0.xxx，RMSE = 0.xxx"
```

### 问题重述短语
```
- "...是...领域的核心问题之一"
- "现有方法主要面临以下挑战："
- "（1）...（2）...（3）..."
- "本文旨在解决上述问题，具体包括："
```

### 模型建立短语
```
- "基于...原理，本节建立...模型"
- "设...为...，...为...，则..."
- "由...公式可得："
- "目标函数定义为："
- "约束条件包括："
```

### 模型求解短语
```
- "采用...算法对上述模型进行求解"
- "算法参数设置如下：..."
- "经过...次迭代，目标函数收敛至..."
- "求解过程如图X所示"
```

### 结果分析短语
```
- "由表X可知，..."
- "从图X可以看出，..."
- "结果表明，...与...的吻合度较高"
- "经计算，...的误差为..."
- "对比分析发现，..."
```

### 模型检验短语
```
- "模型的R² = 0.xxxx，表明..."
- "调整后的R² = 0.xxxx"
- "均方根误差(RMSE)为..."
- "Durbin-Watson统计量DW = ...，表明残差中..."
- "Shapiro-Wilk正态性检验..."
- "方差膨胀因子(VIF)值均小于..."
```

### 灵敏度分析短语
```
- "采用Sobol全局灵敏度分析方法，..."
- "参数...是影响最大的因素，贡献了...%的总输出方差"
- "相比之下，...的影响最小(S1 = ...)"
- "Morris筛选方法提供了互补的分析视角"
- "蒙特卡洛模拟(10000次采样)得到..."
```

### 模型评价短语
```
- "本文模型的优点包括："
- "模型具有...的精度，..."
- "模型在...方面仍有改进空间"
- "未来可考虑引入...以提高..."
```

### 结论短语（CRITICAL：禁止分点）

**结论的撰写格式与摘要一致：必须使用连续自然段落，严禁使用任何形式的分点编号。**

**禁止的格式（以下任一形式均不允许出现在结论中）：**
- 编号列表：(1)...(2)...(3)...
- 项目符号：- ... - ... - ...
- 数字序号：1. ... 2. ... 3. ...
- 显式引出语："主要结论如下：" 后接分点

**正确的格式：** 结论由2-3个自然段落组成，每个子问题的结论通过自然语言衔接（如"在此基础上..."、"进一步扩展到..."、"最后..."），形成连贯的叙述流。第一段概括全文并融合各子问题结果，第二段（可选）总结模型检验发现和推广价值。

**正确示例——结论的结构模板：**

第一段：本文针对...问题，建立了...模型，采用...方法对五个子问题进行了系统求解，并进行了模型检验与灵敏度分析。在...条件下，...为...。采用...算法对...参数进行优化后，...可达...。在此基础上，通过...，将...提升至...，较...提升...%。进一步扩展到...场景，...，总...为...。最后针对...问题，通过...策略，总...为...，实现了...。

第二段：模型检验方面，...验证显示...，验证了...的可靠性。...灵敏度分析表明...是最敏感参数（...），...次之（...），...影响最小（...）。蒙特卡洛模拟（...次）得到...95%置信区间为[...]，...概率为...%，表明...。本文的模型和优化方法可推广至...，为...提供了定量参考。

**关键原则：**
- 结论与摘要数值完全一致，但不简单复制摘要文本
- 结论比摘要更详细，包含具体参数值和检验结果
- 不引入正文中未出现的新内容
- 每个子问题的结论通过过渡词自然衔接，读起来像一篇完整的短文

### 学术表述模板
```
- "由表X可知，...呈...趋势"
- "从图X可以直观地看出，..."
- "计算结果表明，...与...基本一致"
- "经对比分析，...的精度优于..."
- "综合以上分析，本文得出以下结论："
- "需要指出的是，...存在一定的局限性"
```
