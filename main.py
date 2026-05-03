import streamlit as st
import pandas as pd
st.set_page_config(page_title="Finanças", page_icon="💰")

st.markdown('''
# Boas Vindas!
            
# Nosso app financeiro
            
Solução para organização financeira           
'''
)
file_upload = st.file_uploader(label="faça upload dos dados", type=["csv"])
if file_upload:

    df = pd.read_csv(file_upload)
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date

    columns_fmt = {"valor":st.column_config.NumberColumn("valor", format="$%d")}

    st.dataframe(df, hide_index=True, column_config=columns_fmt)


    df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")
    st.dataframe(df_instituicao)
