import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# CONFIGURAÇÃO E ESTILIZAÇÃO VISUAL (CSS)
# ==============================================================================
st.set_page_config(
    page_title="Calculadora Bayesiana Pro",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .metric-card-positive { border-left-color: #2ca02c; }
    .metric-card-warning { border-left-color: #ff7f0e; }
    .metric-title { font-size: 0.85rem; color: #6c757d; font-weight: bold; margin-bottom: 5px; }
    .metric-value { font-size: 1.6rem; font-weight: bold; color: #212529; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Calculadora Bayesiana & Análise de Falso Alarme")
st.caption("Plataforma Interativa para Análise de Testes Diagnósticos e Atualização Sequencial")

# ==============================================================================
# MENU LATERAL: CENÁRIOS E PARÂMETROS
# ==============================================================================
st.sidebar.header("⚙️ Configurações & Parâmetros")

# Presets de cenários práticos
cenario = st.sidebar.selectbox(
    "Carregar Cenário Prático",
    ["Personalizado", "Rastreamento Médico (Câncer de Mama)", "Inspeção Industrial (Componente Deituoso)", "Teste de Segurança / Intrusão"]
)

# Valores padrão dependendo do cenário
if cenario == "Rastreamento Médico (Câncer de Mama)":
    default_prev, default_sens, default_fp = 0.800, 90.0, 7.0
elif cenario == "Inspeção Industrial (Componente Deituoso)":
    default_prev, default_sens, default_fp = 0.050, 99.0, 1.0
elif cenario == "Teste de Segurança / Intrusão":
    default_prev, default_sens, default_fp = 0.010, 95.0, 3.0
else:
    default_prev, default_sens, default_fp = 0.100, 99.0, 5.0

st.sidebar.markdown("---")

prev_input = st.sidebar.number_input(
    "Prevalência Populacional P(D) (%)",
    min_value=0.001, max_value=100.0, value=default_prev, step=0.010, format="%.3f"
)
sens_input = st.sidebar.slider("Sensibilidade P(T⁺|D) (%)", 50.0, 100.0, default_sens, 0.1)
fp_input = st.sidebar.slider("Taxa de Falso Alarme P(T⁺|Dᶜ) (%)", 0.01, 20.0, default_fp, 0.05)

# Conversões decimais
P_D = prev_input / 100.0
P_Sens = sens_input / 100.0
P_FP = fp_input / 100.0

# Cálculos fundamentais do 1º Teste
P_T1_pos = (P_Sens * P_D) + (P_FP * (1 - P_D))
P_Posteriori_T1 = (P_Sens * P_D) / P_T1_pos if P_T1_pos > 0 else 0.0

# ==============================================================================
# NAVEGAÇÃO POR ABAS
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Diagnóstico Único & Amostra", 
    "📈 Curva de Sensibilidade", 
    "🔄 Testes Sequenciais", 
    "📚 Casos Práticos & Teoria"
])

# ------------------------------------------------------------------------------
# ABA 1: DIAGNÓSTICO ÚNICO & VISUALIZAÇÃO POPULACIONAL
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("1. Visão Geral do Teste Único")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="metric-card"><div class="metric-title">PREVALÊNCIA A PRIORI</div>
                    <div class="metric-value">{prev_input:.3f}%</div></div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="metric-card"><div class="metric-title">SENSIBILIDADE</div>
                    <div class="metric-value">{sens_input:.1f}%</div></div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="metric-card metric-card-warning"><div class="metric-title">FALSO ALARME</div>
                    <div class="metric-value">{fp_input:.2f}%</div></div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div class="metric-card metric-card-positive"><div class="metric-title">POSTERIORI P(D|T⁺)</div>
                    <div class="metric-value">{P_Posteriori_T1 * 100:.2f}%</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Decomposição em amostra hipotética de 100.000 indivíduos
    st.subheader("Decomposição Prática em uma Amostra de 100.000 Pessoas/Lotes")
    N = 100_000
    doentes = N * P_D
    sadios = N * (1 - P_D)
    
    VP = doentes * P_Sens           # Verdadeiros Positivos
    FN = doentes * (1 - P_Sens)     # Falsos Negativos
    FP = sadios * P_FP              # Falsos Positivos
    VN = sadios * (1 - P_FP)        # Verdadeiros Negativos

    col_chart, col_table = st.columns([1.2, 1])
    
    with col_chart:
        df_pop = pd.DataFrame({
            "Categoria": ["Verdadeiros Positivos (VP)", "Falsos Positivos (FP)", "Verdadeiros Negativos (VN)", "Falsos Negativos (FN)"],
            "Quantidade": [VP, FP, VN, FN],
            "Status": ["Positivo Real", "Falso Positivo", "Negativo Real", "Falso Negativo"]
        })
        fig_bar = px.bar(
            df_pop, x="Categoria", y="Quantidade", color="Status",
            title="Distribuição Absoluta de Resultados para N=100.000",
            text_auto='.0f',
            color_discrete_map={"Positivo Real": "#2ca02c", "Falso Positivo": "#ff7f0e", "Negativo Real": "#1f77b4", "Falso Negativo": "#d62728"}
        )
        fig_bar.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_table:
        st.markdown(f"""
        **Resumo Numérico da População:**
        * **Total com a Condição:** `{int(doentes):,}`
        * **Total Sem a Condição:** `{int(sadios):,}`
        * **Testes Positivos Totais:** `{int(VP + FP):,}`
          * **Verdadeiros Positivos (Possuem a condição):** `{int(VP):,}`
          * **Falsos Positivos (Alarme Falso):** `{int(FP):,}`
        
        > **Conclusão:** Dos **{int(VP + FP):,}** indivíduos que testaram positivo, apenas **{int(VP):,}** realmente têm a condição. Isso explica por que o Valor Preditivo Positivo (Posteriori) é de apenas **{P_Posteriori_T1 * 100:.2f}%**.
        """)

# ------------------------------------------------------------------------------
# ABA 2: CURVA DE SENSIBILIDADE E IMPACTO DO FALSO ALARME
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("2. Curva $P(D\vert{}T^+)$ vs. Prevalência Populacional")
    st.write("Demonstração visual do impacto devastador da taxa de falso alarme em condições raras ($0.001\\%$ a $20\\%$).")

    # Gerar vetor de prevalências (0.001% a 20%)
    p_range = np.linspace(0.00001, 0.20, 1000)
    
    # Calcular curvas para diferentes taxas de Falso Alarme
    fig_curve = go.Figure()
    
    taxas_fp_comparacao = [P_FP, 0.01, 0.03, 0.05, 0.10]
    taxas_fp_comparacao = sorted(list(set(taxas_fp_comparacao)))
    
    for fp_val in taxas_fp_comparacao:
        y_vals = (P_Sens * p_range) / ((P_Sens * p_range) + (fp_val * (1 - p_range)))
        is_current = (fp_val == P_FP)
        fig_curve.add_trace(go.Scatter(
            x=p_range * 100, y=y_vals * 100,
            mode='lines',
            name=f'Falso Alarme = {fp_val*100:.2f}% {"(Atual)" if is_current else ""}',
            line=dict(width=3 if is_current else 1.5, dash='solid' if is_current else 'dot')
        ))

    # Adicionar o ponto atual do usuário
    fig_curve.add_trace(go.Scatter(
        x=[prev_input], y=[P_Posteriori_T1 * 100],
        mode='markers+text',
        name='Configuração Atual',
        marker=dict(color='red', size=12, symbol='circle'),
        text=[f"  ({prev_input:.3f}%, {P_Posteriori_T1*100:.1f}%)"],
        textposition="top left"
    ))

    fig_curve.update_layout(
        title="Probabilidade a Posteriori em Função da Prevalência",
        xaxis_title="Prevalência Populacional P(D) (%)",
        yaxis_title="Probabilidade a Posteriori P(D|T⁺) (%)",
        xaxis=dict(range=[0, 20]),
        yaxis=dict(range=[0, 105]),
        hovermode="x unified",
        height=450
    )
    
    st.plotly_chart(fig_curve, use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 3: TESTES SEQUENCIAIS DINÂMICOS
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("3. Módulo de Atualização Bayesiana Sequencial")
    st.write("Simule múltiplos testes independentes em sequência. A probabilidade a posteriori de cada teste torna-se a priori do teste seguinte.")

    num_testes = st.slider("Número de Testes Sequenciais Independentes", min_value=1, max_value=5, value=3)
    
    # Lista para salvar o histórico de atualização
    historico_priori = [P_D]
    historico_posteriori = []
    
    p_atual = P_D
    for i in range(num_testes):
        p_teste_pos = (P_Sens * p_atual) + (P_FP * (1 - p_atual))
        p_post = (P_Sens * p_atual) / p_teste_pos
        historico_posteriori.append(p_post)
        if i < num_testes - 1:
            p_atual = p_post
            historico_priori.append(p_atual)

    # Gráfico de evolução sequencial
    df_seq = pd.DataFrame({
        "Teste": [f"Teste {i+1}" for i in range(num_testes)],
        "Priori (%)": [p * 100 for p in historico_priori],
        "Posteriori (%)": [p * 100 for p in historico_posteriori]
    })

    fig_seq = go.Figure()
    fig_seq.add_trace(go.Bar(
        x=df_seq["Teste"], y=df_seq["Posteriori (%)"],
        text=[f"{val:.2f}%" for val in df_seq["Posteriori (%)"]],
        textposition='auto',
        marker_color='#1f77b4',
        name="Posteriori P(D|T⁺)"
    ))

    fig_seq.update_layout(
        title="Evolução da Certeza do Diagnóstico a Cada Teste Positivo Consecutivo",
        yaxis_title="Probabilidade (%)",
        yaxis=dict(range=[0, 105]),
        height=400
    )

    st.plotly_chart(fig_seq, use_container_width=True)
    
    st.dataframe(df_seq.style.format({"Priori (%)": "{:.3f}%", "Posteriori (%)": "{:.2f}%"}), use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 4: CASOS PRÁTICOS & FUNDAMENTAÇÃO
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("📚 Fundamentação Teórica & Estudos de Caso")
    
    st.latex(r"""
    P(D \mid T^+) = \frac{P(T^+ \mid D) \cdot P(D)}{P(T^+ \mid D) \cdot P(D) + P(T^+ \mid D^c) \cdot (1 - P(D))}
    """)

    with st.expander("Estudo de Caso 1: Rastreamento Médico de Doenças Raras"):
        st.write("""
        Em exames médicos populacionais (como mamografias ou testes virais em assintomáticos), a prevalência é muito baixa ($\le 1\%$). 
        Mesmo que o teste tenha $99\%$ de sensibilidade, um falso alarme de $5\%$ gera mais falsos positivos totais do que verdadeiros doentes, reduzindo o Valor Preditivo Positivo (VPP) para menos de $20\%$.
        """)

    with st.expander("Estudo de Caso 2: Controle de Qualidade Industrial"):
        st.write("""
        Em linhas de produção automatizadas de altíssima precisão, a taxa de componentes defeituosos é de apenas $0,05\%$.
        Um sistema de visão computacional com $1\%$ de falso alarme descartará indevidamente muitos componentes bons se um segundo teste confirmatório não for realizado.
        """)

    with st.expander("Estudo de Caso 3: Sistemas de Detecção de Intrusão (Cibersegurança)"):
        st.write("""
        Em redes corporativas, a imensa maioria dos pacotes de dados é legítima. Um IDS (System Intrusion Detection) com taxa de falso alarme baixa ainda assim gera dezenas de alertas falsos diários devido ao imenso volume de tráfego, exigindo análise sequencial antes de bloquear o acesso de um usuário.
        """)
