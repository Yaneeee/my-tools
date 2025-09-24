import os
import time
from collections import Counter
from typing import List, Tuple

import pandas as pd
from pandas import DataFrame
from pulp import LpProblem, LpVariable, LpMinimize, LpInteger, lpSum, LpStatus, value


def get_combine(
        spec_list: List[int], semi_spec_list: List[int], loss_4: int, loss_8: int
) -> Tuple[DataFrame, List[int]]:
    """
    组合spec_list，满足子集的和在半成品的规格[i-max_loss,i] for i in semi_spec_list内
    :param spec_list: 需求规格列表
    :param semi_spec_list: 半成品规格列表
    :param loss_4: 组合长度小于4的成品宽度损耗
    :param loss_8: 组合长度大于等于4的成品宽度损耗
    :return: pd.DataFrame, 满足条件的组合
    """
    res = []
    lens = []
    # 遍历半成品规格
    for i in semi_spec_list:
        _res = subset_sum_i(spec_list, i, loss_4, loss_8)
        res.extend(_res)
        lens.append(len(_res))

    # 分析组合结果
    _res_df = analyze_arr_res(spec_list, res)

    return _res_df, lens


def backtrack(
        state: List[int], target: int, choices: List[int], start: int, res: List[List[int]], loss_4: int,loss_8: int
):
    """回溯算法：子集和 I"""
    if len(state) <= 4:
        # 子集长度小于等于4时且和在 [0,loss_8] 内，记录解
        if 0 <= target <= loss_8:
            res.append(list(state))
            return
    elif 4 < len(state) < 9:
        # 子集长度大于4时且和在 [0,loss_8] 内，记录解
        if loss_4 <= target <= loss_8:
            res.append(list(state))
            return
    else:
        # 子集长度大于9时，不记录解
        return

    # 遍历所有选择
    # 剪枝二：从 start 开始遍历，避免生成重复子集
    for i in range(start, len(choices)):
        # 剪枝一：若子集和超过 target ，则直接结束循环
        # 这是因为数组已排序，后边元素更大，子集和一定超过 target
        if target - choices[i] < 0:
            break
        # 尝试：做出选择，更新 target, start
        state.append(choices[i])
        # 进行下一轮选择
        backtrack(state, target - choices[i], choices, i, res, loss_4, loss_8)
        # 回退：撤销选择，恢复到之前的状态
        state.pop()


def subset_sum_i(nums: List[int], target: int, loss_4=None, loss_8=None) -> List[List[int]]:
    """求解子集和 I"""
    state = []  # 状态（子集）
    nums.sort()  # 对 nums 进行排序
    start = 0  # 遍历起始点
    res = []  # 结果列表（子集列表）
    backtrack(state, target, nums, start, res, loss_4, loss_8)
    return res


def analyze_arr_res(spec_list: List[int], _res: List[List[int]]):
    """
    分析组合结果
    :param spec_list: 需求规格列表
    :param _res: 满足条件的组合
    :return: pd.DataFrame, 组合分析结果
    """
    rows = []
    for row in _res:
        counts = Counter(row)
        rows.append([counts.get(col, 0) for col in spec_list])

    _res_df = pd.DataFrame(rows, columns=spec_list)
    # print(_res_df.dtypes)

    return _res_df


def analyze_indeed_data(_indeed_df: DataFrame) -> DataFrame:
    """
    分析成品需求数据
    :param self: SmartSlit object
    :param _indeed_df: 需求数据
    :return: pd.DataFrame, 成品需求数据分析结果
    """
    indeed_df = _indeed_df.copy()
    # 处理缺失值
    indeed_df[indeed_df.columns[-1]].fillna(999, inplace=True)
    indeed_df.fillna(0, inplace=True)
    # 转换数据类型
    indeed_df = indeed_df.astype(int)
    indeed_df.sort_values(by=['成品规格/mm'], inplace=True)
    # print(indeed_df.dtypes)
    # print(indeed_df)

    return indeed_df


def analyze_semi_data(_semi_df: DataFrame) -> DataFrame:
    """
    分析半成品库存数据
    :param self: SmartSlit object
    :param _semi_df: 半成品库存数据
    :return: pd.DataFrame, 半成品库存数据分析结果
    """
    semi_df = _semi_df.copy()
    # 处理缺失值
    semi_df.fillna(999, inplace=True)
    # 转换数据类型
    semi_df = semi_df.astype(int)
    # print(semi_df.dtypes)
    # print(semi_df)

    return semi_df


def analyze_res(_res: DataFrame,_indeed_df: DataFrame, _x_values: dict) -> Tuple[DataFrame,DataFrame]:
    """
    处理结果
    :param _indeed_df: 成品需求数据
    :param _res: 组合分析结果
    :param _x_values: 组合方案
    :return: count_res, cut_df 分切数量分析结果，刀组分析结果
    """
    res = _res.loc[_x_values.keys(), :]
    cols = res.columns.tolist()
    values = _x_values.values()

    cut_arrs = []
    for i in range(len(res)):
        cut_arr = '+'.join(f'{w}x{n}' for w,n in zip(cols,res.iloc[i, :]) if n > 0)
        cut_sum = sum(map(lambda m, n: m * n, cols, res.iloc[i, :]))
        cut_arrs.append(f'{cut_arr}={cut_sum}')
    # print(cut_arrs)
    # print(cut_sums)
    cut_df = pd.DataFrame({'刀组': cut_arrs, '刀数': values})
    # print(cut_df)

    # print(res)
    indeed_df = _indeed_df.copy()
    del indeed_df[indeed_df.columns[-1]]
    for col in res.columns:
        # print(col)
        # print(res.loc[:,col])
        count = sum(map(lambda m, n: m * n, res.loc[:,col], values))
        indeed_df.loc[indeed_df[indeed_df.columns[0]] == col,'分切数量/R'] = count

    indeed_df['留库数量/R'] = list(map(lambda l, m, n: l + m - n, indeed_df['库存数量/R'], indeed_df['分切数量/R'], indeed_df['需求数量/R']))
    count_res = indeed_df.astype(int)
    # print(count_res)
    return count_res, cut_df


def export_report(count_res, cut_res):
    """
    导出报告
    :param count_res: 分切数量分析结果
    :param cut_res: 刀组分析结果
    :return: DataFrame, 报告数据
    """
    # 导出报告
    output_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_file = f'排刀方案_{output_time}.xlsx'
    # 保存结果到excel文件
    with pd.ExcelWriter(output_file) as writer:
        count_res.to_excel(writer, sheet_name="分切统计", index=False)
        cut_res.to_excel(writer, sheet_name="排刀组合", index=False)

    return os.path.abspath(output_file)

def save_data(_indeed_df: DataFrame):
    """
    保存需求数据
    :param _indeed_df: 需求数据
    :return:
    """
    if _indeed_df.empty:
        return
    output_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_file = f'需求数据_{output_time}.csv'
    # 保存结果到csv文件
    _indeed_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    return output_file



class SmartSlit:
    """
    input:
        - _indeed_df: pd.DataFrame,成品需求数据, columns: ['规格', '需求', '库存','增量限制']
        - _semi_df: pd.DataFrame,半成品库存数据, columns: ['规格', '库存']
    output: SmartSlit object
    """

    def __init__(self, _indeed_df: DataFrame, _semi_df: DataFrame, _loss_4: int, _loss_8: int):
        # 需求数据
        self.indeed_df = analyze_indeed_data(_indeed_df)
        # 半成品库存数据
        self.semi_df = analyze_semi_data(_semi_df)
        # 损耗限制
        # 一刀4颗成品的半成品宽度损耗限制
        self.loss_4 = _loss_4
        # 一刀8颗成品的半成品宽度损耗限制
        self.loss_8 = _loss_8

    def get_indeed_cut_combine(self) -> Tuple[DataFrame, List[int]]:
        """
        找出成品需求数据组合使和满足半成品宽度及损耗限制
        :param self: SmartSlit object
        :return: pd.DataFrame,list, 满足条件的组合和组合长度
        """
        # 获取规格列表
        self.spec_list = self.indeed_df['成品规格/mm'].tolist()
        # 获取半成品规格
        self.semi_spec_list = self.semi_df['半成品规格/mm'].tolist()
        # 回溯算法组合spec_list，满足子集的和在半成品的规格内
        res, lens = get_combine(self.spec_list, self.semi_spec_list, self.loss_4, self.loss_8)

        return res, lens

    def cal_arr(self, res: DataFrame, lens: List[int]):
        """
        计算满足需求的组合方案
        :param lens: 各宽幅半成品能分切的刀组组合长度
        :param res: 满足条件的组合
        :return:
        """
        # 半成品规格库存数量
        self.semi_num = self.semi_df['库存数量/R'].tolist()

        # 设置问题模型
        prob = LpProblem("分切排刀辅助工具", LpMinimize)

        # 定义变量
        x = [LpVariable(f"x_{i:08d}", 0, None, LpInteger) for i in range(len(res))]

        # 目标函数, 最小化刀组数量
        prob += lpSum(x)

        # 约束条件一，半成品约束
        for i, _len in enumerate(lens):
            prob += lpSum(x[j] for j in range(lens[i - 1] if i > 0 else 0, lens[i - 1] + _len if i > 0 else _len)) <= \
                    self.semi_num[i]

        # 约束条件二，成品约束
        for i in range(len(self.spec_list)):
            # 当需求数量大于库存数量时，统计值大于等于需求数量-库存数量
            cut_nums = list(map(lambda m, n: m * n, res[self.indeed_df.iloc[i, 0]], x))

            indeed_num = self.indeed_df.iloc[i, 1]
            kucun_num = self.indeed_df.iloc[i, 2]
            if self.indeed_df.iloc[i]['需求数量/R'] > self.indeed_df.iloc[i]['库存数量/R']:
                prob += lpSum(cut_nums) >= indeed_num - kucun_num
            # 当需求数量小于等于库存数量时，统计值大于等于0
            else:
                prob += lpSum(cut_nums) >= 0

            # 约束条件三，增量约束
            limit_num = self.indeed_df.iloc[i, 3]
            if 0 <= limit_num < 999:
                prob += lpSum(cut_nums) <= indeed_num - kucun_num + limit_num

        # 调用求解器求解
        pro_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        # 输出lp文件
        # prob.writeLP(f'./res/{pro_time}.lp')
        # 复杂问题调用glpk.exe求解器求解
        # solver = GLPK_CMD(path='./glpk/w32/glpsol.exe', msg=False)
        # prob.solve(solver)
        # 简单问题直接求解
        prob.solve()

        # 输出结果
        if LpStatus[prob.status] == 'Optimal':
            min_num = value(prob.objective)
            x_values = {}
            for i in range(len(x)):
                if value(x[i]) > 0:
                    x_values[i] = value(x[i])

            return min_num, x_values
        else:
            return None, None

    def analyze_result(self, res: DataFrame, x_values: dict)-> Tuple[DataFrame, DataFrame]:
        """
        分析结果
        :param res: 满足条件的组合
        :param x_values: 组合方案
        :return: count_res, cut_df 分切数量分析结果，刀组分析结果
        """
        return analyze_res(res, self.indeed_df, x_values)