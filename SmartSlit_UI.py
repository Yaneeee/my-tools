import os

import pandas as pd
import streamlit as st

from SmartSlit import SmartSlit, export_report, save_data

st.set_page_config(page_title="分切排刀辅助工具", page_icon=":material/split_scene_left:")

st.title("分切排刀辅助工具")

st.write('使用教程请查看左侧边栏')

with open('./help.md', 'r', encoding='utf-8') as f:
    st.sidebar.markdown(f.read())

st.subheader("输入损耗：")
col1, col2 = st.columns(2)
with col1:
    loss_4 = st.number_input("一刀切4颗半成品损耗/mm", value=5, step=5)
with col2:
    loss_8 = st.number_input("一刀切8颗半成品损耗/mm", value=10, step=5)

if loss_4 > loss_8:
    st.error("一刀切4颗半成品损耗不能大于一刀切8颗半成品损耗！")

st.subheader("输入半成品数据：")
st.write('半成品库存数量可以不填')

semi_info = pd.DataFrame(columns=["半成品规格/mm", "库存数量/R"], data=[], dtype=int)

semi_data = st.data_editor(data=semi_info, num_rows="dynamic", width='stretch')

st.subheader("输入成品需求数据：")

default_df = pd.DataFrame(columns=["成品规格/mm", "需求数量/R", "库存数量/R", "增量限制/R"], data=[], dtype=int)
indeed_file = st.file_uploader("上传需求数据……", type=["csv"])

default_length = st.number_input('默认收卷米数/M：', value=2000, step=100)

if indeed_file is not None:
    default_df = pd.read_csv(indeed_file, encoding='utf-8-sig')

indeed_data = st.data_editor(data=default_df, num_rows="dynamic", width='stretch')

sum_area = (indeed_data.fillna(0).iloc[:, 0].astype(int) * indeed_data.fillna(0).iloc[:, 1].astype(int)).sum(
    skipna=True) * default_length / 1000
if sum_area:
    st.info(f'订单需求面积：{sum_area}㎡')

indeed_data_csv = save_data(indeed_data)
if indeed_data_csv is not None:
    with open(indeed_data_csv, 'rb') as f:
        st.download_button(label="保存需求数据", data=f, file_name=os.path.basename(indeed_data_csv),)
if st.button("开始分切排刀", type="primary"):
    # 计算分切排刀方案
    smart_slit = SmartSlit(indeed_data, semi_data, loss_4, loss_8)

    res,lens = smart_slit.get_indeed_cut_combine()
    # 计算方案
    min_num,x = smart_slit.cal_arr(res,lens)
    # 分析结果
    if min_num is not None:
        st.success(f"排刀成功，最小半成品消耗：{min_num} 卷，共{len(x)}个刀组。")
        # 分析结果
        count_res, cut_res = smart_slit.analyze_result(res, x)
        st.subheader("分切排刀结果：")
        st.dataframe(count_res)
        st.dataframe(cut_res)
        # 输出报表
        report_file = export_report(count_res, cut_res)

        with open(report_file, 'rb') as f:
            st.download_button(label="下载报表", data=f, file_name=os.path.basename(report_file),icon="📥")
    else:
        st.error("无可行方案，请调整后再试！")
