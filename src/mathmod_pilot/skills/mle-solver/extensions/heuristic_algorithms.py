"""
启发式优化算法模块 — mle-solver 扩展
遗传算法(GA)、粒子群优化(PSO)、模拟退火(SA)、差分进化(DE)
所有算法返回 (最优解, 最优值, 收敛历史) 三元组

Original-Source : MathMod-Pilot Project
Repository      : https://github.com/scipilot/mathmod_pilot
License         : MIT
"""
from __future__ import annotations

import logging

import numpy as np
from typing import Callable, Tuple, List, Optional, Dict, Any
import warnings

logger = logging.getLogger(__name__)


# ============================================================
# 1. 遗传算法 (Genetic Algorithm)
# ============================================================
def genetic_algorithm(
    objective_func: Callable,
    bounds: List[Tuple[float, float]],
    pop_size: int = 100,
    n_generations: int = 200,
    crossover_prob: float = 0.8,
    mutation_prob: float = 0.1,
    elite_ratio: float = 0.05,
    early_stop_generations: int = 30,
    random_state: Optional[int] = None,
    verbose: bool = True,
) -> Tuple[np.ndarray, float, List[float]]:
    """
    遗传算法求解连续优化问题
    
    Parameters
    ----------
    objective_func : 目标函数 f(x) -> float，求最小值
    bounds : 各维度的 (lower, upper)
    pop_size : 种群大小
    n_generations : 最大迭代代数
    crossover_prob : 交叉概率
    mutation_prob : 变异概率
    elite_ratio : 精英保留比例
    early_stop_generations : 早停代数（最优值不再改进时停止）
    random_state : 随机种子
    verbose : 是否打印进度
    
    Returns
    -------
    (best_solution, best_fitness, history)
    """
    rng = np.random.RandomState(random_state)
    n_dim = len(bounds)
    bounds_arr = np.array(bounds)
    
    # 初始化种群
    population = rng.uniform(
        bounds_arr[:, 0], bounds_arr[:, 1], size=(pop_size, n_dim)
    )
    
    fitness = np.array([objective_func(ind) for ind in population])
    best_idx = np.argmin(fitness)
    best_solution = population[best_idx].copy()
    best_fitness = fitness[best_idx]
    history = [best_fitness]
    
    n_elite = max(1, int(pop_size * elite_ratio))
    stagnation_counter = 0
    
    for gen in range(n_generations):
        # 精英保留
        elite_indices = np.argsort(fitness)[:n_elite]
        new_population = [population[i].copy() for i in elite_indices]
        
        # 生成新个体
        while len(new_population) < pop_size:
            # 锦标赛选择
            tournament_size = 3
            tournament = rng.choice(pop_size, size=tournament_size, replace=False)
            parent1_idx = tournament[np.argmin(fitness[tournament])]
            tournament = rng.choice(pop_size, size=tournament_size, replace=False)
            parent2_idx = tournament[np.argmin(fitness[tournament])]
            
            parent1 = population[parent1_idx]
            parent2 = population[parent2_idx]
            
            # 交叉（模拟二进制交叉 SBX）
            if rng.rand() < crossover_prob:
                eta = 20  # 分布指数
                u = rng.rand(n_dim)
                beta = np.where(
                    u <= 0.5,
                    (2 * u) ** (1 / (eta + 1)),
                    (1 / (2 * (1 - u))) ** (1 / (eta + 1)),
                )
                child1 = 0.5 * ((1 + beta) * parent1 + (1 - beta) * parent2)
                child2 = 0.5 * ((1 - beta) * parent1 + (1 + beta) * parent2)
            else:
                child1 = parent1.copy()
                child2 = parent2.copy()
            
            # 变异（多项式变异）
            for child in [child1, child2]:
                if rng.rand() < mutation_prob:
                    eta_m = 20
                    for j in range(n_dim):
                        if rng.rand() < 1.0 / n_dim:
                            delta = rng.rand()
                            if delta < 0.5:
                                delta_q = (2 * delta) ** (1 / (eta_m + 1)) - 1
                            else:
                                delta_q = 1 - (2 * (1 - delta)) ** (1 / (eta_m + 1))
                            child[j] += delta_q * (bounds[j][1] - bounds[j][0]) * 0.1
                
                # 边界约束
                child = np.clip(child, bounds_arr[:, 0], bounds_arr[:, 1])
                new_population.append(child)
        
        population = np.array(new_population[:pop_size])
        fitness = np.array([objective_func(ind) for ind in population])
        
        current_best_idx = np.argmin(fitness)
        current_best = fitness[current_best_idx]
        
        if current_best < best_fitness:
            best_fitness = current_best
            best_solution = population[current_best_idx].copy()
            stagnation_counter = 0
        else:
            stagnation_counter += 1
        
        history.append(best_fitness)
        
        if verbose and gen % 20 == 0:
            logger.info("GA Gen %4d: best=%.6e, avg=%.6e", gen, best_fitness, fitness.mean())
        
        if stagnation_counter >= early_stop_generations:
            if verbose:
                logger.info("GA early-stop at gen %d, no improvement for %d gens", gen, early_stop_generations)
            break
    
    return best_solution, best_fitness, history


# ============================================================
# 2. 粒子群优化 (Particle Swarm Optimization)
# ============================================================
def particle_swarm_optimization(
    objective_func: Callable,
    bounds: List[Tuple[float, float]],
    n_particles: int = 50,
    n_iterations: int = 200,
    w: float = 0.7,          # 惯性权重
    c1: float = 1.5,         # 认知系数
    c2: float = 1.5,         # 社会系数
    early_stop_iterations: int = 30,
    random_state: Optional[int] = None,
    verbose: bool = True,
) -> Tuple[np.ndarray, float, List[float]]:
    """
    粒子群优化算法求解连续优化问题
    
    Parameters
    ----------
    objective_func : 目标函数 f(x) -> float，求最小值
    bounds : 各维度的 (lower, upper)
    n_particles : 粒子数量
    n_iterations : 最大迭代次数
    w : 惯性权重
    c1 : 认知系数（个体最优吸引力）
    c2 : 社会系数（全局最优吸引力）
    early_stop_iterations : 早停迭代数
    random_state : 随机种子
    verbose : 是否打印进度
    
    Returns
    -------
    (best_position, best_value, history)
    """
    rng = np.random.RandomState(random_state)
    n_dim = len(bounds)
    bounds_arr = np.array(bounds)
    
    # 初始化
    positions = rng.uniform(bounds_arr[:, 0], bounds_arr[:, 1], size=(n_particles, n_dim))
    velocities = rng.uniform(-0.1, 0.1, size=(n_particles, n_dim)) * (bounds_arr[:, 1] - bounds_arr[:, 0])
    
    p_best_positions = positions.copy()
    p_best_values = np.array([objective_func(pos) for pos in positions])
    
    g_best_idx = np.argmin(p_best_values)
    g_best_position = p_best_positions[g_best_idx].copy()
    g_best_value = p_best_values[g_best_idx]
    history = [g_best_value]
    
    stagnation_counter = 0
    
    for it in range(n_iterations):
        # 线性递减惯性权重
        w_current = w - (w - 0.4) * it / n_iterations
        
        for i in range(n_particles):
            r1, r2 = rng.rand(n_dim), rng.rand(n_dim)
            
            velocities[i] = (w_current * velocities[i]
                           + c1 * r1 * (p_best_positions[i] - positions[i])
                           + c2 * r2 * (g_best_position - positions[i]))
            
            # 速度限制
            max_vel = 0.2 * (bounds_arr[:, 1] - bounds_arr[:, 0])
            velocities[i] = np.clip(velocities[i], -max_vel, max_vel)
            
            positions[i] += velocities[i]
            positions[i] = np.clip(positions[i], bounds_arr[:, 0], bounds_arr[:, 1])
            
            # 评估
            current_value = objective_func(positions[i])
            
            if current_value < p_best_values[i]:
                p_best_values[i] = current_value
                p_best_positions[i] = positions[i].copy()
                
                if current_value < g_best_value:
                    g_best_value = current_value
                    g_best_position = positions[i].copy()
                    stagnation_counter = 0
        
        if g_best_value >= history[-1]:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
        
        history.append(g_best_value)
        
        if verbose and it % 20 == 0:
            logger.info("PSO Iter %4d: best=%.6e", it, g_best_value)
        
        if stagnation_counter >= early_stop_iterations:
            if verbose:
                logger.info("PSO early-stop at iter %d", it)
            break
    
    return g_best_position, g_best_value, history


# ============================================================
# 3. 模拟退火 (Simulated Annealing)
# ============================================================
def simulated_annealing(
    objective_func: Callable,
    bounds: List[Tuple[float, float]],
    initial_temp: float = 1000.0,
    cooling_rate: float = 0.95,
    n_iterations: int = 1000,
    step_size: float = 0.1,
    restart_count: int = 3,
    random_state: Optional[int] = None,
    verbose: bool = True,
) -> Tuple[np.ndarray, float, List[float]]:
    """
    模拟退火算法求解连续优化问题
    
    Parameters
    ----------
    objective_func : 目标函数 f(x) -> float，求最小值
    bounds : 各维度的 (lower, upper)
    initial_temp : 初始温度
    cooling_rate : 冷却速率 (0~1)
    n_iterations : 每轮温度下的迭代次数
    step_size : 邻域步长比例
    restart_count : 重新加热次数
    random_state : 随机种子
    verbose : 是否打印进度
    
    Returns
    -------
    (best_solution, best_energy, history)
    """
    rng = np.random.RandomState(random_state)
    n_dim = len(bounds)
    bounds_arr = np.array(bounds)
    
    # 初始化
    current = rng.uniform(bounds_arr[:, 0], bounds_arr[:, 1])
    current_energy = objective_func(current)
    
    best_solution = current.copy()
    best_energy = current_energy
    history = [best_energy]
    
    temp = initial_temp
    
    for restart in range(restart_count + 1):
        if restart > 0:
            # 重新加热：随机重启
            current = rng.uniform(bounds_arr[:, 0], bounds_arr[:, 1])
            current_energy = objective_func(current)
            temp = initial_temp * 0.5
            if verbose:
                logger.info("SA reheat #%d, temp=%.1f", restart, temp)
        
        for _ in range(n_iterations):
            # 生成邻域解
            neighbor = current + rng.normal(0, step_size * (bounds_arr[:, 1] - bounds_arr[:, 0]), n_dim)
            neighbor = np.clip(neighbor, bounds_arr[:, 0], bounds_arr[:, 1])
            neighbor_energy = objective_func(neighbor)
            
            delta = neighbor_energy - current_energy
            
            if delta < 0 or rng.rand() < np.exp(-delta / max(temp, 1e-10)):
                current = neighbor
                current_energy = neighbor_energy
                
                if current_energy < best_energy:
                    best_solution = current.copy()
                    best_energy = current_energy
            
            history.append(best_energy)
        
        temp *= cooling_rate
        
        if verbose:
            logger.info("SA T=%.1f: best=%.6e, current=%.6e", temp, best_energy, current_energy)
        
        if temp < 1e-3:
            break
    
    return best_solution, best_energy, history


# ============================================================
# 4. 差分进化 (Differential Evolution) — 额外赠送
# ============================================================
def differential_evolution(
    objective_func: Callable,
    bounds: List[Tuple[float, float]],
    pop_size: int = 50,
    n_generations: int = 200,
    F: float = 0.8,         # 缩放因子
    CR: float = 0.9,        # 交叉概率
    early_stop_generations: int = 30,
    random_state: Optional[int] = None,
    verbose: bool = True,
) -> Tuple[np.ndarray, float, List[float]]:
    """差分进化算法"""
    rng = np.random.RandomState(random_state)
    n_dim = len(bounds)
    bounds_arr = np.array(bounds)
    
    population = rng.uniform(bounds_arr[:, 0], bounds_arr[:, 1], size=(pop_size, n_dim))
    fitness = np.array([objective_func(ind) for ind in population])
    
    best_idx = np.argmin(fitness)
    best_solution = population[best_idx].copy()
    best_fitness = fitness[best_idx]
    history = [best_fitness]
    stagnation = 0
    
    for gen in range(n_generations):
        for i in range(pop_size):
            # 随机选择三个不同个体
            candidates = [j for j in range(pop_size) if j != i]
            a, b, c = rng.choice(candidates, size=3, replace=False)
            
            # 变异
            mutant = population[a] + F * (population[b] - population[c])
            mutant = np.clip(mutant, bounds_arr[:, 0], bounds_arr[:, 1])
            
            # 交叉
            cross_points = rng.rand(n_dim) < CR
            if not np.any(cross_points):
                cross_points[rng.randint(n_dim)] = True
            trial = np.where(cross_points, mutant, population[i])
            
            # 选择
            trial_fitness = objective_func(trial)
            if trial_fitness < fitness[i]:
                population[i] = trial
                fitness[i] = trial_fitness
                if trial_fitness < best_fitness:
                    best_fitness = trial_fitness
                    best_solution = trial.copy()
                    stagnation = 0
        
        if best_fitness >= history[-1]:
            stagnation += 1
        else:
            stagnation = 0
        
        history.append(best_fitness)
        
        if verbose and gen % 20 == 0:
            logger.info("DE Gen %4d: best=%.6e", gen, best_fitness)
        
        if stagnation >= early_stop_generations:
            if verbose:
                logger.info("DE early-stop at gen %d", gen)
            break
    
    return best_solution, best_fitness, history


# ============================================================
# 5. 统一接口
# ============================================================
def solve_optimization(
    objective_func: Callable,
    bounds: List[Tuple[float, float]],
    method: str = "auto",
    **kwargs,
) -> Tuple[np.ndarray, float, Dict[str, Any]]:
    """
    统一优化求解接口
    
    Parameters
    ----------
    objective_func : 目标函数
    bounds : 参数边界
    method : 算法选择
        - "auto": 自动选择（<5维用PSO，>=5维用DE）
        - "ga": 遗传算法
        - "pso": 粒子群优化
        - "sa": 模拟退火
        - "de": 差分进化
    **kwargs : 传递给具体算法的参数
    
    Returns
    -------
    (solution, value, info) 其中 info 包含 history, method, n_evals
    """
    if method == "auto":
        method = "pso" if len(bounds) < 5 else "de"
    
    methods = {
        "ga": genetic_algorithm,
        "pso": particle_swarm_optimization,
        "sa": simulated_annealing,
        "de": differential_evolution,
    }
    
    if method not in methods:
        raise ValueError(f"未知方法: {method}，可选: {list(methods.keys())}")
    
    solver = methods[method]
    solution, value, history = solver(objective_func, bounds, **kwargs)
    
    return solution, value, {
        "method": method,
        "history": history,
        "n_evals": len(history),
        "converged": len(history) < kwargs.get("n_generations", kwargs.get("n_iterations", 200)),
    }


if __name__ == "__main__":
    # 测试：Rastrigin 函数
    def rastrigin(x):
        return 10 * len(x) + sum(xi**2 - 10 * np.cos(2 * np.pi * xi) for xi in x)
    
    bounds = [(-5.12, 5.12)] * 5
    
    print("=== 遗传算法 ===")
    sol, val, hist = genetic_algorithm(rastrigin, bounds, pop_size=50, n_generations=100, verbose=False)
    print(f"最优解: {sol}, 最优值: {val:.6f}")
    
    print("\n=== 粒子群优化 ===")
    sol, val, hist = particle_swarm_optimization(rastrigin, bounds, n_particles=30, n_iterations=100, verbose=False)
    print(f"最优解: {sol}, 最优值: {val:.6f}")
    
    print("\n=== 差分进化 ===")
    sol, val, hist = differential_evolution(rastrigin, bounds, pop_size=30, n_generations=100, verbose=False)
    print(f"最优解: {sol}, 最优值: {val:.6f}")
    
    print("\n=== 统一接口 ===")
    sol, val, info = solve_optimization(rastrigin, bounds, method="auto", verbose=False)
    print(f"方法: {info['method']}, 最优值: {val:.6f}")