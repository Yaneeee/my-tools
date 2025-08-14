import streamlit as st
author = "Yaneeee"
mail = "yanyi_1995@163.com"

pg = st.navigation([st.Page("SmartSlit_UI.py",title='分切排刀辅助工具',icon=':material/split_scene_left:'),
                    st.Page("RollDiameterCalculation.py",title='卷径计算工具',icon=':material/measuring_tape:'),
                    st.Page("Palletization.py",title='拼箱打包计算工具',icon=':material/pallet:'),
                    ])
st.markdown(f"> 作者：@{author}，邮箱：{mail}")
pg.run()