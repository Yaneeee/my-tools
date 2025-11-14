import pandas as pd
import streamlit as st

from SlitRangeFunc import subset_sum_i, res_2_df

st.set_page_config(page_title="排刀组合计算", page_icon=":material/width_normal:")

st.title("排刀组合计算")

st.subheader("输入半成品/大膜卷宽幅/mm：")

semi_info = pd.DataFrame(columns=["规格/mm"], data=[])

semi_data = st.data_editor(data=semi_info, num_rows="dynamic", width='stretch')
cut_loss = st.slider("可接受损耗/%", value=0, min_value=0, max_value=10, step=1) / 100

st.subheader("输入成品需求数据：")

default_df = pd.DataFrame(columns=["成品规格/mm"], data=[])

indeed_data = st.data_editor(data=default_df, num_rows="dynamic", width="stretch")

if st.button("开始组合", type="primary"):

    indeed_width_list = indeed_data.astype(int)["成品规格/mm"].tolist()
    semi_width_list = semi_data.astype(int)["规格/mm"].tolist()

    _res = []
    for semi in semi_width_list:
        res = subset_sum_i(indeed_width_list, semi, cut_loss)
        _res.extend(res)

    cut_df = res_2_df(indeed_width_list, _res)
    st.write(f'共有{len(cut_df)}个组合')
    st.write(cut_df)
