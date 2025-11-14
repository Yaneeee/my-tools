import math
from collections import Counter

import pandas as pd


def backtrack(
        state: list[int], target: int, choices: list[int], start: int, res: list[list[int]], max_loss: int):
    """回溯算法：子集和 I"""
    # 子集和等于 target 时，记录解
    # if target == 0:
    #     res.append(list(state))
    #     return
    _len = len(state)
    # if 0 <= target - (_len + 2) * thickness < min_num:
    if _len > 0 and target <= max_loss:
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
        backtrack(state, target - choices[i], choices, i, res, max_loss)
        # 回退：撤销选择，恢复到之前的状态
        state.pop()


def subset_sum_i(nums: list[int], target: int, cut_loss: float) -> list[list[int]]:
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
    start = 0  # 遍历起始点
    res = []  # 结果列表（子集列表）
    max_loss = math.ceil(target * cut_loss)
    backtrack(state, target, nums, start, res, max_loss)
    # print(res)
    return res


def res_2_df(nums: list[int], res: list[list[int]]) -> pd.DataFrame:
    """将结果列表转化为 DataFrame"""
    _dic = []
    for row in res:
        counts = Counter(row)
        num = [counts.get(i, 0) for i in nums]
        cut_arr = '+'.join(f'{m}x{n}' for m, n in zip(nums, num) if n > 0)
        cut_sum = sum(row)
        _dic.append(f'{cut_arr}={cut_sum}')
    res_df = pd.DataFrame(columns=["成品规格/mm"], data=_dic)
    return res_df
