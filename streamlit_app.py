import streamlit as st

pg = st.navigation([st.Page("SmartSlit_UI.py",title='分切排刀辅助工具',icon=':material/content_cut:'),
                    st.Page("RollDiameterCalculation.py",title='卷径计算工具',icon=':material/measuring_tape:')])

pg.run()