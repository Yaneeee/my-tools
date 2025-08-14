from collections import Counter

import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, LpInteger, lpSum, LpStatus, value


def backtrack(
        state: list[int], target: int, choices: list[int], start: int, res: list[list[int]], thickness: int,
        min_num: int
):
    """回溯算法：子集和 I"""
    # 子集和等于 target 时，记录解
    # if target == 0:
    #     res.append(list(state))
    #     return
    _len = len(state)
    if 0 <= target - (_len + 2) * thickness <= min_num:
        res.append(list(state))
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
        backtrack(state, target - choices[i], choices, i, res, thickness, min_num)
        # 回退：撤销选择，恢复到之前的状态
        state.pop()


def subset_sum_i(nums: list[int], target: int, thickness: int) -> list[list[int]]:
    """
    求解子集和 I
    :param nums: 元素列表
    :param target: 最大值
    :param thickness: 厚度
    :return:
    """
    """求解子集和 I"""
    state = []  # 状态（子集）
    nums.sort()  # 对 nums 进行排序
    min_num = min(nums)
    start = 0  # 遍历起始点
    res = []  # 结果列表（子集列表）
    backtrack(state, target, nums, start, res, thickness, min_num)
    # print(res)
    return res


def res_2_df(nums: list[int], res: list[list[int]]) -> pd.DataFrame:
    """将结果列表转化为 DataFrame"""
    rows = []
    for row in res:
        counts = Counter(row)
        rows.append([counts.get(i, 0) for i in nums])

    df = pd.DataFrame(rows, columns=nums)
    return df


def calc_range(indeed_widths: list[int], indeed_nums: list[int], res: pd.DataFrame, more: int):
    # 设置方程，求解
    prob = LpProblem("堆叠打托", LpMinimize)

    # 定义变量
    x = [LpVariable(f"x_{i:08d}", 0, None, LpInteger) for i in range(res.shape[0])]
    # print(x)

    # 目标函数
    prob += lpSum(x)

    # 约束条件
    for i in range(len(indeed_widths)):
        # 打包数量
        pack_nums = list(map(lambda m, n: m * n, res[indeed_widths[i]], x))
        # print(pack_nums)
        prob += lpSum(pack_nums) >= indeed_nums[i]
        prob += lpSum(pack_nums) <= indeed_nums[i] + more

    # 调用求解器
    prob.solve()
    # prob.writeLP("stacking_pallet_packer.lp")

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


class StackingPalletPacker:

    def __init__(self, indeed_df: pd.DataFrame, pack_height: int, pallet_height: int, thickness: int):
        # 输入数据
        self._indeed_df = indeed_df
        # print(self._indeed_df)
        # 规格宽度
        self._indeed_widths = self._indeed_df["规格/mm"].tolist()
        # print(self._indeed_widths)
        # 需求数量
        self._indeed_nums = self._indeed_df["订单数量/R"].tolist()
        # 托盘高度
        self._pallet_height = pallet_height
        # 打托高度
        self._target = pack_height - pallet_height
        # 包材厚度
        self._t = thickness
        # 所有的组合
        self._combines_df = self.get_combines()
        # print(self._combines_df)

    def get_combines(self):
        # 所有可能的组合
        _all_combines = subset_sum_i(self._indeed_widths, self._target, self._t)
        _combines_df = res_2_df(self._indeed_widths, _all_combines)
        return _combines_df

    def calculate_arr(self, more: int = 0):
        _min_num, _x_values = calc_range(self._indeed_widths, self._indeed_nums, self._combines_df, more)
        # print(_min_num, _x_values)
        return _min_num, _x_values

    def get_result(self, more: int = 0):
        _min_num, _x_values = self.calculate_arr(more)
        if _min_num is None:
            return None
        else:
            res_combine = self._combines_df.loc[_x_values.keys(), :]
            res_df = self._indeed_df.copy()
            for i in range(len(self._indeed_widths)):
                count = sum(map(lambda m, n: m * n, res_combine[self._indeed_widths[i]], _x_values.values()))
                res_df.loc[i, '打包数量/R'] = count
            res_df['差异数量/R'] = res_df['打包数量/R'] - res_df['订单数量/R']

            cols = res_combine.columns.tolist()
            pack_arrs = []
            pack_sums = []
            pack_thicks = []
            pack_totle = []
            for i in range(len(res_combine)):
                pack_arr = '+'.join(f'{w}x{n}' for w, n in zip(cols, res_combine.iloc[i, :]) if n > 0)
                pack_num = res_combine.iloc[i, :].sum()
                # print(pack_num)
                pack_sum = sum(map(lambda m, n: m * n, cols, res_combine.iloc[i, :]))

                pack_arrs.append(pack_arr)
                pack_sums.append(pack_sum)
                pack_thicks.append((pack_num + 2) * self._t)
                pack_totle.append(pack_sum + (pack_num + 2) * self._t + self._pallet_height)
            # print(cut_arrs)
            # print(cut_sums)
            res_combine_parase = pd.DataFrame(
                {'堆组合': pack_arrs, '膜高/mm': pack_sums, '包材/mm': pack_thicks, '总高/mm': pack_totle,
                 '堆数': _x_values.values()})

            return res_combine_parase, res_df
