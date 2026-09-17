# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 15:32:06 2026

@author: Vicenzo
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Calculadora Bayesiana Interativa",
    page_icon="📊",
    layout="wide"
)

# Estilização visual dos gráficos
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.grid'] = True

st.title("📊 Calculadora Bayesiana Interativa")
st.markdown("""
**Análise de Sensibilidade ao Falso Alarme e Atualização Sequencial**  
Esta aplicação calcula a probabilidade a posteriori de um evento/doença dado um teste positivo, $P(D\vert{}T^+)$, utilizando o Teorema de Bayes.
""")

# ==============================================================================
# PAINEL LATERAL: CONFIGURAÇÃO DE PARÂMETROS (REQUISITO 1)
# ==============================================================================
st.sidebar.header("⚙️ Parâmetros do Teste")

# 1. Prevalência P(D)
prevalencia_pct = st.sidebar.number_input(
    "Prevalência Populacional P(D) (%)",
    min_value=0.001,
    max_value=100.0,
    value=0.100,
    step=0.010,
    format="%.3f",
    help="Probabilidade a priori de possuir a condição antes de realizar o teste."
)

# 2. Sensibilidade P(T+|D)
sensibilidade_pct = st.sidebar.slider(
    "Sensibilidade P(T⁺|D) (%)",
    min_value=50.0,
    max_value=100.0,
    value=99.0,
    step=0.1,
    help="Taxa de Verdadeiro Positivo (probabilidade de dar positivo quando a condição está presente)."
)

# 3. Falso Alarme P(T+|D^c)
falso_alarme_pct = st.sidebar.slider(
    "Taxa de Falso Alarme P(T⁺|Dᶜ) (%)",
    min_value=0.01,
    max_value=20.0,
    value=5.0,
    step=0.05,
    help="Taxa de Falso Positivo (1 - Especificidade)."
)

# Conversão para probabilidades decimais
P_D = prevalencia_pct / 100.0
P_T_given_D = sensibilidade_pct / 100.0
P_T_given_Dc = falso_alarme_pct / 100.0

# Cálculo do Teorema de Bayes para o 1º Teste
P_T1 = (P_T_given_D * P_D) + (P_T_given_Dc * (1 - P_D))
P_D_given_T1 = (P_T_given_D * P_D) / P_T1

# ==============================================================================
# DASHBOARD PRINCIPAL: PAINEL DE MÉTRICAS INICIAIS
# ==============================================================================
st.header("1. Diagnóstico de Teste Único")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Prevalência a Priori P(D)", f"{prevalencia_pct:.3f}%")
col2.metric("Sensibilidade P(T⁺|D)", f"{sensibilidade_pct:.1f}%")
col3.metric("Falso Alarme P(T⁺|Dᶜ)", f"{falso_alarme_pct:.2f}%")
col4.metric("Posteriori P(D|T⁺) [VPP]", f"{P_D_given_T1 * 100:.2f}%")

st.info(f"""
**Interpretação:** Mesmo com uma sensibilidade de **{sensibilidade_pct}%**, devido à baixa prevalência (**{prevalencia_pct}%**) e ao falso alarme (**{falso_alarme_pct}%**), a chance real do indivíduo/lote testado ser positivo após **1 teste positivo** é de apenas **{P_D_given_T1 * 100:.2f}%**.
""")

# ==============================================================================
# REQUISITO 2: CURVA P(D|T+) EM FUNÇÃO DA PREVALÊNCIA (0.001% a 20%)
# ==============================================================================
st.header("2. Análise de Sensibilidade: Curva $P(D\vert{}T^+)$ vs. Prevalência")

# Amplitude de prevalência de 0.001% a 20%
p_array = np.linspace(0.00001, 0.20, 1000)
p_post_array = (P_T_given_D * p_array) / ((P_T_given_D * p_array) + (P_T_given_Dc * (1 - p_array)))

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(p_array * 100, p_post_array * 100, color='#1f77b4', lw=2.5, 
        label=fr'Falso Alarme $P(T^+\vert{}D^c) = {falso_alarme_pct}\%$')

# Destaque do ponto atual
ax.plot(prevalencia_pct, P_D_given_T1 * 100, 'ro', markersize=8, label=f'Ponto Atual ({prevalencia_pct:.3f}%, {P_D_given_T1*100:.2f}%)')
ax.axvline(x=prevalencia_pct, color='red', linestyle='--', alpha=0.5)
ax.axhline(y=P_D_given_T1 * 100, color='red', linestyle='--', alpha=0.5)

ax.set_title(r'Impacto do Falso Alarme em Condições Raras ($0.001\%$ a $20\%$ de Prevalência)', fontsize=12, fontweight='bold')
ax.set_xlabel('Prevalência Populacional P(D) (%)', fontsize=10)
ax.set_ylabel('Probabilidade a Posteriori P(D|T⁺) (%)', fontsize=10)
ax.set_xlim(0, 20)
ax.set_ylim(0, 105)
ax.legend(loc='lower right')

st.pyplot(fig)

# ==============================================================================
# REQUISITO 3: ATUALIZAÇÃO SEQUENCIAL BAYESIANA
# ==============================================================================
st.header("3. Módulo de Testes em Sequência (Atualização Sequencial)")

st.write("""
Demonstração de como a **probabilidade a posteriori** do $1^o$ teste torna-se a **probabilidade a priori** do $2^o$ teste confirmatório independente.
""")

# Cálculo do 2º Teste Confirmatório
P_D_priori_test2 = P_D_given_T1
P_T2 = (P_T_given_D * P_D_priori_test2) + (P_T_given_Dc * (1 - P_D_priori_test2))
P_D_given_T2 = (P_T_given_D * P_D_priori_test2) / P_T2

# Exibição em duas colunas comparativas
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("📋 1º Teste Diagnóstico")
    st.markdown(f"""
    * **Priori Inicial $P(D)_1$:** `{prevalencia_pct:.3f}%`
    * **Sensibilidade $P(T_1^+\vert{}D)$:** `{sensibilidade_pct:.1f}%`
    * **Falso Alarme $P(T_1^+\vert{}D^c)$:** `{falso_alarme_pct:.2f}%`
    * **Posteriori $P(D\vert{}T_1^+)$:** **`{P_D_given_T1 * 100:.2f}%`**
    """)

with col_t2:
    st.subheader("🔬 2º Teste Confirmatório")
    st.markdown(f"""
    * **Nova Priori $P(D)_2 = P(D\vert{}T_1^+)$:** `{P_D_priori_test2 * 100:.2f}%`
    * **Sensibilidade $P(T_2^+\vert{}D)$:** `{sensibilidade_pct:.1f}%`
    * **Falso Alarme $P(T_2^+\vert{}D^c)$:** `{falso_alarme_pct:.2f}%`
    * **Posteriori Final $P(D\vert{}T_1^+, T_2^+)$:** **`{P_D_given_T2 * 100:.2f}%`**
    """)

st.success(f"""
**Conclusão da Atualização Sequencial:**  
Após dois testes positivos consecutivos independentes, a probabilidade do diagnóstico ser correto passa de **{P_D_given_T1 * 100:.2f}%** no 1º teste para **{P_D_given_T2 * 100:.2f}%** no 2º teste.
""")