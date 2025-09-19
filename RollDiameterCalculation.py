import math

import streamlit as st
from CAL import calculate_diameter, calculate_length

st.set_page_config(page_title="卷径计算工具", page_icon=':material/measuring_tape:')
st.title('卷径计算工具')

choice = st.radio('请选择：',['卷径计算','长度计算'],horizontal=True)

d0 = st.selectbox('纸管大小(英寸/inch):',[3,6])
thickness = st.number_input('材料厚度(微米/μm):',min_value=10,value=100,step=5)


if choice=='卷径计算':
    # 已知长度厚度计算卷径
    # st.write(choice)

    length = st.number_input('长度(米/M):',step=10)
    if length>0:
        D = calculate_diameter(length,thickness,d0)
        w = (1+math.sqrt(2)*2+math.sqrt(3))/math.sqrt(2) * D/2
        st.info(f'长度为{length}M的膜卷，卷径约: {D:.1f}cm，四颗一层最小托盘尺寸约: {D*2:.1f}x{D*2:.1f}cm, 三颗一层最小托盘尺寸约: {w:.1f}x{w:.1f}cm')
else:
    # 已知卷径厚度计算长度
    # st.write(choice)

    D = st.number_input('卷径(厘米/cm):',min_value=d0*2.54+2.8,step=0.1)
    if D>d0:
        length = calculate_length(D,thickness,d0)
        st.info(f'卷径为{D:.1f}cm的膜卷，长度约: {length:.0f}M')