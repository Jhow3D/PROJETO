import pandas as pd
import streamlit as st
import plotly.express as px


# dataframes para gráficos:

dados_agencias = pd.read_csv('data/agencias.csv')
dados_clientes = pd.read_csv('data/clientes.csv')
dados_colaborador_ag = pd.read_csv("data/colaborador_agencia.csv")
dados_colaboradores = pd.read_csv('data/colaboradores.csv')
dados_contas = pd.read_csv("data/contas.csv")
dados_propostas_cred = pd.read_csv("data/propostas_credito.csv")
dados_transacoes = pd.read_csv("data/transacoes.csv")
dados_transacoes['data_transacao'] = pd.to_datetime(dados_transacoes['data_transacao'],format='mixed')


# PROCESSO DE ANÁLISE:

qtd_agencia = dados_agencias.groupby('cidade',as_index=False)['cod_agencia'].nunique()
qtd_ag_estado = dados_agencias.groupby('uf',as_index=False)['cod_agencia'].nunique()
qtd_ag_tipo = dados_agencias.groupby('tipo_agencia',as_index=False)['cod_agencia'].nunique()

conta_agencia = pd.merge(dados_contas,dados_agencias[['cod_agencia','nome','tipo_agencia']],on='cod_agencia',how='left')
qtd_clientes_ag = conta_agencia.groupby(['cod_agencia','nome','tipo_agencia'])['cod_cliente'].nunique().sort_values()
qtd_clientes_ag = qtd_clientes_ag.reset_index()

qtd_tipo_conta = conta_agencia.groupby('tipo_agencia')['cod_cliente'].nunique().sort_values(ascending=False)
qtd_tipo_conta = qtd_tipo_conta.reset_index()

qtd_propost = dados_propostas_cred.groupby('status_proposta')['cod_cliente'].nunique().sort_values(ascending=True)
qtd_propost = qtd_propost.reset_index()

df_agenc_status = pd.merge(dados_propostas_cred,dados_colaborador_ag,on='cod_colaborador',how='left')
df_agenc_status = pd.merge(df_agenc_status,dados_agencias,on='cod_agencia',how='left')
qtd_agenc_status = df_agenc_status.groupby(['cod_agencia','nome','status_proposta'])['cod_proposta'].nunique()
qtd_agenc_status = qtd_agenc_status.reset_index()
qtd_agenc_status = qtd_agenc_status.sort_values(by='cod_proposta',ascending=False)
qtd_agenc_status["total_propostas"] = qtd_agenc_status.groupby("nome")["cod_proposta"].transform("sum")
qtd_agenc_status = qtd_agenc_status.sort_values(by="total_propostas", ascending=False)

qtd_agenc_status_geral = df_agenc_status.groupby(['cod_agencia','nome'])['cod_proposta'].nunique().sort_values(ascending=False)
qtd_agenc_status_geral = qtd_agenc_status_geral.reset_index()


dados_transacoes['valor_transacao'] = pd.to_numeric(dados_transacoes['valor_transacao'], errors='coerce')
dados_transacoes['trimestre'] = dados_transacoes['data_transacao'].dt.to_period('Q')
transacoes_por_trimestre = dados_transacoes.groupby('trimestre')['cod_transacao'].count()
volume_por_trimestre = dados_transacoes.groupby('trimestre')['valor_transacao'].sum()
trimestre_mais_transacoes = transacoes_por_trimestre.idxmax()
mais_transacoes = transacoes_por_trimestre.max()
trimestre_maior_volume = volume_por_trimestre.idxmax()
maior_volume = volume_por_trimestre.max()
volume_por_trimestre = volume_por_trimestre.reset_index()
transacoes_por_trimestre = transacoes_por_trimestre.reset_index()   


dados_transacoes['mes'] = dados_transacoes['data_transacao'].dt.month_name()
dados_transacoes['mes_com_r'] = dados_transacoes['mes'].apply(lambda x: 'com R' if 'r' in x.lower() else 'sem R')
transacoes_com_r_total = dados_transacoes.groupby(['mes_com_r'])['cod_transacao'].count()
transacoes_com_r_total = transacoes_com_r_total.reset_index()

transacoes_com_r_d_c = dados_transacoes.groupby(['mes_com_r','nome_transacao'])['cod_transacao'].count()
transacoes_com_r_d_c = transacoes_com_r_d_c.reset_index()
transacoes_com_r_d_c = transacoes_com_r_d_c[transacoes_com_r_d_c['nome_transacao'].str.contains('Compra')]

# DASHBOARD:

#GRAFICO 1 - QUANTIDADE DE AGENCIAS

fig_qtd_gencia = px.bar(
    qtd_agencia,
    x='cidade',
    y='cod_agencia',
    title='Quantidade de Agências por Cidade',
    text='cod_agencia'
)
fig_qtd_gencia.update_traces(
    textposition='outside'
)
fig_qtd_gencia.update_layout(
    title_x=0.3,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Quantidade de Agências',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,
    xaxis = dict(showticklabels=True),
    yaxis = dict(showticklabels=False)
)
st.write(fig_qtd_gencia)

#GRAFICO 2 - QUANTIDADE DE AGENCIAS POR ESTADO

fig_qtd_ag_estado = px.bar(
    qtd_ag_estado,
    x='uf',
    y='cod_agencia',
    title='Quantidade de Agências por Estado',
    text='cod_agencia'
)
fig_qtd_ag_estado.update_traces(
    textposition='outside'
)
fig_qtd_ag_estado.update_layout(
    title_x=0.3,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Quantidade de Agências',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,
    xaxis = dict(showticklabels=True),
    yaxis = dict(showticklabels=False)
)
st.write(fig_qtd_ag_estado)

#GRAFICO 3 - DISTRIBUIÇÃO DE AGÊNCIA POR TIPO

fig_ag_tipo = px.pie(
    qtd_ag_tipo,
    names='tipo_agencia',
    values='cod_agencia',
    title='Distribuição de Agências por Tipo',
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_ag_tipo.update_traces(
    textinfo='percent+label',
    pull=[0.05] * len(qtd_ag_tipo)  # Destaca levemente todas as fatias
)
fig_ag_tipo.update_layout(
    title_x=0.3,
    legend_title="Tipo de Agência",
    font=dict(size=14),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)
st.write(fig_ag_tipo)

#GRAFICO 4 - QUANTIDADE DE CLIENTES POR AGÊNCIA

fig_conta_ag = px.bar(
    qtd_clientes_ag,
    x='nome',
    y='cod_cliente',
    title='Quantidade de Clientes por Agência',
    text='cod_cliente'
)
fig_conta_ag.update_layout(
    title_x=0.5,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Quantidade de Clientes',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,
    xaxis = dict(showticklabels=True),
    yaxis = dict(showticklabels=False)
)
st.write(fig_conta_ag)

#GRAFICO 5 - QUANTIDADE DE CONTAS POR TIPO

fig_tipo_conta = px.pie(
    qtd_tipo_conta,
    names='tipo_agencia',
    values='cod_cliente',
    title='Quantidade de Contas por Tipo',
    hole=0.3,
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_tipo_conta.update_traces(
    textinfo='percent+label',
    pull=[0.05] * len(qtd_ag_tipo)  # Destaca levemente todas as fatias
)
fig_tipo_conta.update_layout(
    title_x=0.5,
    legend_title="Tipo de Agência",
    font=dict(size=14),
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)

st.write(fig_tipo_conta)

#GRAFICO 6 - QUANTIDADE DE PROPOSTAS POR STATUS

fig_qtd_propost = px.bar(
    qtd_propost,
    x='cod_cliente',
    y='status_proposta',
    title='Quantidade de Propostas por Status',
    labels={'status_proposta':'status da proposta','cod_cliente':'quantidade de clientes'},
    text='cod_cliente',
    orientation='h'
)
fig_qtd_propost.update_layout(
    title_x=0.5,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Status da Proposta',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,)
st.write(fig_qtd_propost)

#GRAFICO 7 - QUANTIDADE DE PROPOSTAS POR AGÊNCIA E STATUS
fig_qtd_agencia = px.bar(
    qtd_agenc_status,
    x='nome',  # Eixo X: Código da agência
    y='cod_proposta',  # Eixo Y: Quantidade de propostas
    color='status_proposta',  # Segmentação por status da proposta
    title='Quantidade de Propostas por Agência e Status',
    text='cod_proposta',  # Texto com a quantidade de propostas
    barmode='stack'  # Barras empilhadas
)

fig_qtd_agencia.update_layout(title_x=0.5, xaxis_title='Código da Agência', yaxis_title='Quantidade de Propostas')
st.write(fig_qtd_agencia)

#GRAFICO 8 - QUANTIDADE DE PROPOSTAS POR AGêNCIA
fig_qtd_ag_status = px.bar(
    qtd_agenc_status_geral,
    x='nome',
    y='cod_proposta',
    title='Quantidade de Propostas por Agência',
    text='cod_proposta'
)

fig_qtd_ag_status.update_layout(
    title_x=0.5,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Quantidade de Propostas',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,
    xaxis = dict(showticklabels=True),
    yaxis = dict(showticklabels=False)
)
st.write(fig_qtd_ag_status) 


#GRAFICO 9 - QUANTIDADE DE TRANSAÇÕES POR TRIMESTRE

transacoes_por_trimestre['trimestre'] = transacoes_por_trimestre['trimestre'].astype(str)
fig_transacao_trimestre = px.bar(
    transacoes_por_trimestre,
    x='trimestre',
    y='cod_transacao',
    title='Quantidade de Transações por Trimestre',
    text='cod_transacao'
)
fig_transacao_trimestre.update_layout(
    title_x=0.5,  # Centraliza o título
    xaxis_title='',
    yaxis_title='Quantidade de Transações',
    xaxis_title_standoff=10,
    yaxis_title_standoff=10,
    xaxis = dict(showticklabels=True),
    yaxis = dict(showticklabels=False)
)
st.write(fig_transacao_trimestre)

#GRAFICO 10 - EVOLUÇÃO DAS TRANSAÇÕES POR TRIMESTRE

volume_por_trimestre['trimestre'] = volume_por_trimestre['trimestre'].astype(str)
fig_volume_trismestre = px.line(
    volume_por_trimestre,
    x='trimestre',
    y='valor_transacao',
    title='Evolução das Transações por Trimestre',
    markers=True,  # Adiciona pontos para destacar os trimestres
    line_shape='spline',  # Deixa a linha mais suave
    color_discrete_sequence=['#1f77b4']  # Define uma cor personalizada
)
fig_volume_trismestre.update_layout(
    title_x=0.5,  # Centraliza o título
    xaxis_title='Trimestre',
    yaxis_title='Valor da Transação (R$)',  # Adiciona o símbolo da moeda
    xaxis=dict(
        tickangle=-45,  # Inclina os rótulos do eixo X para evitar sobreposição
        showgrid=False,
        ),
    yaxis=dict(
        showgrid=True,  # Mantém grade no eixo Y para melhor visualização
        gridcolor='lightgray',  # Deixa a grade mais sutil
        tickprefix='R$ ',  # Adiciona prefixo da moeda no eixo Y
        tickformat=".2f",# Mantém duas casas decimais
        dtick = 500000
    ),
    # plot_bgcolor='white',  # Fundo branco para um visual mais limpo
)
st.write(fig_volume_trismestre)


#GRAFICO 11 - TRANSAÇÕES POR TIPO: MESES COM "R" VS MESES SEM "R"


fig_transacoes_empilhadas = px.bar(
    transacoes_com_r_total,
    x='mes_com_r',
    y='cod_transacao',    # Categorias dentro das barras
    title='Movimentações nos Meses:',
    labels={'mes_com_r': 'Categoria do Mês', 'cod_transacao': 'Número de Transações'},
    text_auto=True,  # Exibe os valores dentro das barras
    barmode='stack',  # Define barras empilhadas
)
fig_transacoes_empilhadas.update_layout(
    title_x=0.1,  # Centraliza o título
    xaxis_title='Tipo de Mês',
    yaxis_title='Número de Transações',
    # plot_bgcolor='white',  # Fundo branco para visual limpo
    yaxis=dict(showgrid=True, gridcolor='lightgray')  # Mantém a grade no Y
)


# GRAFICO 11 - TRANSAÇÕES DE CRÉDITO E DÉBITO (COM R vs SEM R)
# coluna 'tipo_transacao' para separar Crédito e Débito
transacoes_com_r_d_c['tipo_transacao'] = transacoes_com_r_d_c['nome_transacao'].apply(
    lambda x: 'Crédito' if 'Crédito' in x else 'Débito'
)

# Criar gráfico de barras agrupadas
fig_transacoes_r_d_C = px.bar(
    transacoes_com_r_d_c,
    x='mes_com_r',              # Eixo X: Mês (com ou sem R)
    y='cod_transacao',          # Eixo Y: Quantidade de transações
    color='tipo_transacao',      # Diferencia Crédito e Débito por cores
    barmode='group',             # Barras lado a lado
    title='Transações de Crédito e Débito (Com R vs Sem R)',
    labels={'mes_com_r': 'Mês', 'cod_transacao': 'Quantidade de Transações'},
    text='cod_transacao',              # Exibe os valores dentro das barras
)

# Melhorar layout
fig_transacoes_r_d_C.update_layout(title_x=0.1, xaxis_title='Categoria (Com R / Sem R)',
                  yaxis_title='Quantidade de Transações',
                  )

col1,col2 = st.columns([3,4])

with col1: 
    st.write(fig_transacoes_empilhadas)

with col2:
    st.write(fig_transacoes_r_d_C)