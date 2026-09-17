# CUMCM Modeling Skills Toolkit 使用指南

## 1. 快速克隆与环境准备

克隆本仓库到本地：
```bash
git clone https://github.com/Fatespur/mathmod-pilot
cd cumcm-modeling-skills
```

安装 Python 科学计算依赖：
```bash
pip install -r requirements.txt
# 或者以开发模式安装包
pip install -e .
```

---

## 2. 模式 A：作为 Agent Skills 使用

本仓库天然遵循 Agent 技能标准规范。每个 Skill 在其对应的目录下包含权威的 `SKILL.md`：

### Claude Desktop / Antigravity / Codex 集成
在 Agent 系统提示词或技能注册表中加载本仓库路径：
```json
{
  "skills_directory": "./skills"
}
```

### 显式提示词唤起示例
```markdown
角色：你是一名国家特等奖水准的数学建模专家。
任务：请根据赛题题目，调用技能 $problem-analyzer 进行赛题形式化拆解。
要求：
1. 提取物理实体、所有变量及其量纲；
2. 建立问题分解图与目标函数；
3. 输出符合规范的 problem_structure.json 与 hard_assertions.json。
```

---

## 3. 模式 B：使用独立 CLI 工具辅助建模

仓库中的许多核心算法和验证工具支持直接命令行调用：

### 3.1 生成学术方法架构图 (Academic Flowchart)
```bash
python skills/06-visualization/cumcm-academic-flowchart/scripts/cumcm_flowchart.py --help
```

### 3.2 论文宏与数值一致性检查 (Numeric Verifier)
```bash
python skills/07-writing/mcm-paper-writing/scripts/paper_number_validator.py --help
```

### 3.3 CUMCM 格式合规性与排版检查 (Format Validator)
```bash
python skills/07-writing/mcm-paper-writing/scripts/cumcm_format_validator.py --help
```

### 3.4 启发式优化算法调用 (GA/PSO/SA)
```python
from skills.04_algorithms_and_solving.mle_solver.extensions.heuristic_algorithms import genetic_algorithm, pso_algorithm

# 定义目标函数
def sphere(x):
    return sum(x**2)

bounds = [(-5.0, 5.0), (-5.0, 5.0)]
best_x, best_val, history = genetic_algorithm(sphere, bounds, pop_size=50, n_generations=100)
print(f"Optimal solution: {best_x}, Value: {best_val}")
```

---

## 4. 模式 C：启动交互式可视化官网

本地预览和浏览交互式全流程官网：
```bash
cd site
npm install
npm run dev
```
打开浏览器访问 `http://localhost:5173` 即可探索全套技能矩阵与交互式工作流。
