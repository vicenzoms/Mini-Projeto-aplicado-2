import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# Configuração da Página
# ==========================================
st.set_page_config(page_title="Calculadora Bayesiana", layout="wide")
st.title("Calculadora Bayesiana Interativa")
st.write("Análise de Sensibilidade ao Falso Alarme e Atualização Sequencial")

# ==========================================
# Menu Lateral (Requisito 1)
# ==========================================
st.sidebar.header("Parâmetros do Teste")

prevalencia_pct = st.sidebar.number_input("Prevalência P(D) (%)", min_value=0.001, max_value=100.0, value=0.1, step=0.01, format="%.3f")
sensibilidade_pct = st.sidebar.slider("Sensibilidade P(T+|D) (%)", 50.0, 100.0, 99.0, 0.1)
falso_alarme_pct = st.sidebar.slider("Falso Alarme P(T+|D^c) (%)", 0.01, 20.0, 5.0, 0.1)

# Conversão para decimal
prev = prevalencia_pct / 100
sens = sensibilidade_pct / 100
f_alarme = falso_alarme_pct / 100

# ==========================================
# Cálculo do 1º Teste
# ==========================================
# P(T+) = (P(T+|D) * P(D)) + (P(T+|D^c) * P(D^c))
prob_teste_pos = (sens * prev) + (f_alarme * (1 - prev))

# P(D|T+) = (P(T+|D) * P(D)) / P(T+)
posteriori_1 = (sens * prev) / prob_teste_pos

st.header("1. Resultado (Teste Único)")
c1, c2, c3 = st.columns(3)
c1.metric("Prevalência P(D)", f"{prevalencia_pct:.3f}%")
c2.metric("Teste Positivo P(T+)", f"{prob_teste_pos*100:.3f}%")
c3.metric("Posteriori P(D|T+)", f"{posteriori_1*100:.2f}%")

# ==========================================
# Gráfico de Sensibilidade (Requisito 2)
# ==========================================
st.header("2. Curva de Probabilidade vs Prevalência")

# Vetor de prevalência de 0.001% a 20%
x_prev = np.linspace(0.00001, 0.20, 500)
# Aplicação do Teorema de Bayes para o vetor
y_post = (sens * x_prev) / ((sens * x_prev) + (f_alarme * (1 - x_prev)))

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x_prev * 100, y_post * 100, color="blue", label=f"Falso Alarme: {falso_alarme_pct}%")

# Marcação do ponto escolhido pelo usuário
ax.axvline(prevalencia_pct, color="red", linestyle="--", alpha=0.5, label="Sua Prevalência")
ax.plot(prevalencia_pct, posteriori_1 * 100, "ro")

ax.set_xlabel("Prevalência P(D) (%)")
ax.set_ylabel("Probabilidade a Posteriori P(D|T+) (%)")
ax.set_xlim(0, 20)
ax.set_ylim(0, 105)
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)

# ==========================================
# Atualização Sequencial (Requisito 3)
# ==========================================
st.header("3. Atualização Sequencial (2 Testes)")
st.write("A probabilidade a posteriori do 1º teste torna-se a priori do 2º teste.")

# O cálculo recomeça usando posteriori_1 como P(D)
prev_2 = posteriori_1
prob_teste_pos_2 = (sens * prev_2) + (f_alarme * (1 - prev_2))
posteriori_2 = (sens * prev_2) / prob_teste_pos_2

c4, c5 = st.columns(2)

with c4:
    st.subheader("1º Teste (Inicial)")
    st.write(f"**Priori:** {prevalencia_pct:.3f}%")
    st.write(f"**Posteriori Final:** {posteriori_1*100:.2f}%")

with c5:
    st.subheader("2º Teste (Confirmatório)")
    st.write(f"**Nova Priori:** {posteriori_1*100:.2f}%")
    st.write(f"**Posteriori Final:** {posteriori_2*100:.2f}%")
