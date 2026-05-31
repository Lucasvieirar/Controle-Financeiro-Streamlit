import streamlit as st
import pandas as pd
import requests
import datetime

@st.cache_data(ttl="1day")
def get_selic():
    url = "https://www.bcb.gov.br/api/servico/sitebcb/historicotaxasjuros"
    resp = requests.get(url)
    df = pd.DataFrame(resp.json()["conteudo"])

    df["DataInicioVigencia"] =pd.to_datetime(df["DataInicioVigencia"]).dt.date
    df["DataFimVigencia"] = pd.to_datetime(df["DataFimVigencia"]).dt.date
    df["DataFimVigencia"] = df["DataFimVigencia"].fillna(datetime.datetime.today().date())

    return df 



def calc_general_stats(df):
    df_data = df.groupby(by="Data")[["Valor"]].sum()
    df_data["lag_1"] = df_data["Valor"].shift(1)
    df_data["Diferença Mensal Abs."] = df_data["Valor"] -  df_data["lag_1"]
    df_data["Média 6M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(6).mean()
    df_data["Média 12M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(12).mean()
    df_data["Média 24M Diferença Mensal Abs."] = df_data["Diferença Mensal Abs."].rolling(24).mean()


    df_data["Diferença Mensal Rel."] =  df_data["Valor"] /  df_data["lag_1"] - 1 

    df_data["Evolução 6M Total"] = df_data["Valor"].rolling(6).apply(lambda x: x.iloc[-1] - x.iloc[0])
    df_data["Evolução 12M Total"] = df_data["Valor"].rolling(12).apply(lambda x: x.iloc[-1] - x.iloc[0])
    df_data["Evolução 24M Total"] = df_data["Valor"].rolling(24).apply(lambda x: x.iloc[-1] - x.iloc[0])

    df_data["Evolução 6M Relativa"] = df_data["Valor"].rolling(6).apply(lambda x: x.iloc[-1] / x.iloc[0])
    df_data["Evolução 12M Relativa"] = df_data["Valor"].rolling(12).apply(lambda x: x.iloc[-1] / x.iloc[0])
    df_data["Evolução 24M Relativa"] = df_data["Valor"].rolling(24).apply(lambda x: x.iloc[-1] / x.iloc[0])

    df_data = df_data.drop("lag_1", axis=1)

    return df_data
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

    exp1 = st.expander("Dados Brutos")
    columns_fmt = {"valor":st.column_config.NumberColumn("valor", format="$%d")}
    exp1.dataframe(df, hide_index=True, column_config=columns_fmt)

    exp2 = st.expander("Instituições")
    df_instituicao = df.pivot_table(index="Data", columns="Instituição", values="Valor")
    tab_data, tab_history, tab_share = exp2.tabs(["Dados", "Histórico", "Distribuição"])
    with tab_data:
        st.dataframe(df_instituicao)

    with tab_history:
        st.line_chart(df_instituicao)

    with tab_share:

        date = st.date_input("Data para distribuição", min_value=df_instituicao.index.min(),
                      max_value=df_instituicao.index.max() )

        if date not in df_instituicao.index:
            st.warning("Entre com uma data válida")
        else:
            st.bar_chart(df_instituicao.loc[date])
  
    exp3 = st.expander("Estatisticas Gerais")
    df_stats = calc_general_stats(df)

    columns_config = {
        "Valor": st.column_config.NumberColumn('Valor', format="R$ %.2f"),
        "Diferença Mensal Abs.": st.column_config.NumberColumn('Diferença Mensal Abs.', format="R$ %.2f"),
        "Média 6M Diferença Mensal Abs.": st.column_config.NumberColumn('Média 6M Diferença Mensal Abs.', format="R$ %.2f"),
        "Média 12M Diferença Mensal Abs.": st.column_config.NumberColumn('Média 12M Diferença Mensal Abs.', format="R$ %.2f"),
        "Média 24M Diferença Mensal Abs.": st.column_config.NumberColumn('Média 24M Diferença Mensal Abs.', format="R$ %.2f"),
        "Evolução 6M Total": st.column_config.NumberColumn('Evolução 6M Total', format="R$ %.2f"),
        "Evolução 12M Total": st.column_config.NumberColumn('Evolução 12M Total', format="R$ %.2f"),
        "Evolução 24M Total" : st.column_config.NumberColumn('Evolução 24M Total', format="R$ %.2f"),
        "Diferença Mensal Rel.": st.column_config.NumberColumn('Diferença Mensal Rel.', format="percent"),
        "Evolução 6M Relativa": st.column_config.NumberColumn('Evolução 6M Relativa', format="percent"),
        "Evolução 12M Relativa": st.column_config.NumberColumn('Evolução 12M Relativa', format="percent"),
        "Evolução 24M Relativa": st.column_config.NumberColumn('Evolução 24M Relativa', format="percent"),


    }
    
    tab_sats, tab_abs, tab_rel = exp3.tabs(tabs=["Dados", "Histórico de Evolução", "Crescimento Relativo"])
    

    with tab_sats:
        st.dataframe(df_stats, column_config=columns_config)

    with tab_abs:
        abs_cols =  ["Diferença Mensal Abs.",
        "Média 6M Diferença Mensal Abs.", 
        "Média 12M Diferença Mensal Abs.",
        "Média 24M Diferença Mensal Abs.",
        ]
        st.line_chart(df_stats[abs_cols])
    
    with tab_rel:
       rel_cols = [
       "Diferença Mensal Rel.",
       "Evolução 6M Relativa",
       "Evolução 12M Relativa",
       "Evolução 24M Relativa",
       ]
       st.line_chart(data=df_stats[rel_cols])
    
    with st.expander("Metas"):
        col1, col2 = st.columns(2)

        data_inicio_meta = col1.date_input("Início da Meta", max_value=df_stats.index.max())

        filter_data = df_stats.index <= data_inicio_meta

        df_stats.index[filter_data][-1]
        data_filtrado = df_stats.index[filter_data][-1]

        custos_fixos = col1.number_input("Custos Fixos", min_value=0., format="%.2f")

        salario_bruto = col2.number_input("Salário Bruto", min_value=0., format="%.2f")
        salario_liq = col2.number_input("Salário Liquido", min_value=0., format="%.2f")

        valor_inicio = df_stats.loc[ data_filtrado]["Valor"]

        col1.markdown(f"**Patrimônio no Início da Meta**: R$ {valor_inicio:.2f}")


        selic_gov = get_selic()
        filter_selic_date = (selic_gov["DataInicioVigencia"] < data_inicio_meta) & (selic_gov["DataFimVigencia"] > data_inicio_meta)
        selic_default = selic_gov[filter_selic_date]["MetaSelic"].iloc[0]

        selic = st.number_input("Selic", min_value=0., value=selic_default, format="%.2f")
        selic_ano = selic / 100
        selic_mes = (selic_ano + 1) ** (1/12) - 1

        rendimento_ano = valor_inicio * selic_ano
        rendimento_mes = valor_inicio * selic_mes

        col1_pot, col2_pot = st.columns(2)
        mensal = salario_liq - custos_fixos +rendimento_mes
        anual = 12*(salario_liq - custos_fixos) + rendimento_ano

        with col1_pot.container(border=True):
            st.markdown(f"""**Potencial Arrecadação Mês**:\n\n R$ {mensal:.2f}""",
                    help = f"{salario_liq:.2f} + (-{custos_fixos:.2f}) + {rendimento_mes:.2f}")
    
        with col2_pot.container(border=True):
            st.markdown(f"""**Potencial Arrecadação Ano**:\n\n R$ {anual:.2f}""",
                    help=f"12 *({salario_liq:.2f} + (-{custos_fixos:.2f})) + {rendimento_ano:.2f}")

        with st.container(border=True):
            col1_meta, col2_meta = st.columns(2)
        
            with col1_meta:
                meta_estipulada = st.number_input("Meta Estipulada",  min_value=0., format="%.2f", value=anual)
            
            with col2_meta: 
                patrimonio_final = meta_estipulada + valor_inicio
                st.markdown(f'Patrimonio Estimado pós meta:\n\n R$ {patrimonio_final:.2f}')
            
       