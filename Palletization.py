import streamlit as st
import pandas as pd

from PalletPack import StackingPalletPacker

st.set_page_config(page_title="拼箱打包计算工具", page_icon=':material/pallet:')
st.title("拼箱打包计算工具")

# 输入参数
# 托盘尺寸：长 x 宽 x 高
st.sidebar.subheader("托盘尺寸")
L = st.sidebar.slider("长(mm)", value=1100, min_value=600, max_value=1500, step=10)
W = st.sidebar.slider("宽(mm)", value=1100, min_value=600, max_value=1500, step=10)
H = st.sidebar.slider("高(mm)", value=150, min_value=120, max_value=200, step=10)

# 装箱高度
st.sidebar.subheader("装箱高度")
H_box = st.sidebar.slider("高度(mm)", value=2270*2//3, min_value=H, max_value=2270, step=10)

# 包材厚度
st.sidebar.subheader("包材厚度")
t = st.sidebar.slider("厚度(mm)", value=10, min_value=10, max_value=20, step=1)

st.write("托盘尺寸：", L, "mm x", W, "mm x", H, "mm")
st.write("装箱高度：", H_box, "mm")

# 规格数据
st.subheader("规格数据")
# 输入数据
df = pd.DataFrame(columns=["规格/mm","订单数量/R","打包数量/R","差异数量/R"],data=[])

input_df = st.data_editor(df,num_rows='dynamic',use_container_width=True)

indeed_df = input_df.copy()
# 处理缺失值
indeed_df[indeed_df.columns[-1]].fillna(999, inplace=True)
indeed_df.fillna(0, inplace=True)
# 转换数据类型
indeed_df = indeed_df.astype(int)
indeed_df.sort_values(by=['规格/mm'], inplace=True)

if st.checkbox('允许多打包'):
    more = st.slider('多打包数量', value=1, min_value=1, max_value=10, step=1)
else:
    more = 0

st.info("注：当无法刚好满足装满规格，请勾选。")

# 计算
if st.button("计算",type="primary"):
    calculator = StackingPalletPacker(indeed_df,H_box,H,t)
    min_pack,combine_arr = calculator.calculate_arr(more)
    st.write("最小打包数量：",min_pack)
    result_combine,result_df = calculator.get_result(more)
    st.write("打包结果：")
    st.dataframe(result_df,use_container_width=True)
    st.write("打包方案：")
    st.dataframe(result_combine,use_container_width=True,hide_index=True)



