import math


def calculate_diameter(length_meters, thickness_microns, core_diameter_inches, gap=1):
    """
    根据纸的长度、厚度和纸管内径计算卷径

    参数:
    length_meters (float): 纸的长度（米）
    thickness_microns (float): 纸的厚度（微米）
    core_diameter_inches (float): 纸管内径（英寸）

    返回:
    float: 卷径（厘米）
    """
    # 单位转换
    length_cm = length_meters * 100  # 转换为厘米
    thickness_cm = thickness_microns / 10000  # 转换为厘米
    core_radius_cm = core_diameter_inches * 2.54 / 2 + 1  # 转换为厘米,纸管厚度

    # 空隙系数
    # gap = 1.03

    # 计算卷径
    term = (length_cm * thickness_cm * gap) / math.pi
    diameter = 2 * math.sqrt(core_radius_cm ** 2 + term)

    return diameter


def calculate_length(diameter_cm, thickness_microns, core_diameter_inches, gap=1):
    """
    根据卷径、纸的厚度和纸管内径计算纸的长度

    参数:
    diameter_cm (float): 卷径（厘米）
    thickness_microns (float): 纸的厚度（微米）
    core_diameter_inches (float): 纸管内径（英寸）

    返回:
    float: 纸的长度（米）
    """
    # 单位转换
    thickness_cm = thickness_microns / 10000  # 转换为厘米
    core_radius_cm = core_diameter_inches * 2.54 / 2 + 1.4  # 转换为厘米
    outer_radius_cm = diameter_cm / 2  # 外半径（厘米）

    # 空隙系数
    # gap = 1.03

    # 计算长度
    length_cm = (math.pi * (outer_radius_cm ** 2 - core_radius_cm ** 2)) / (thickness_cm * gap)
    length_meters = length_cm / 100  # 转换为米

    return length_meters


# 示例使用
if __name__ == "__main__":
    # 已知长度和厚度，计算卷径
    length = 1000  # 1000米
    thickness = 50  # 50微米
    core_diameter = 3  # 3英寸纸管

    diameter = calculate_diameter(length, thickness, core_diameter)
    print(f"长度 {length} 米，厚度 {thickness} 微米，纸管内径 {core_diameter} 英寸的卷径是: {diameter:.2f} 厘米")

    # 已知卷径和厚度，计算长度
    diameter = 30  # 30厘米卷径
    thickness = 50  # 50微米
    core_diameter = 6  # 6英寸纸管

    length = calculate_length(diameter, thickness, core_diameter)
    print(f"卷径 {diameter} 厘米，厚度 {thickness} 微米，纸管内径 {core_diameter} 英寸的长度是: {length:.2f} 米")