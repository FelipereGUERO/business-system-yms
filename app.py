import os
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Business System - YMS",
    page_icon="🚛",
    layout="wide"
)

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "yms_operacao.csv")

COLUNAS = [
    "id",
    "placa",
    "transportadora",
    "tipo_operacao",
    "doca",
    "status",
    "nota_fiscal",
    "motorista",
    "data_agendada",
    "hora_agendada",
    "hora_entrada",
    "hora_saida",
    "observacoes",
    "ultima_atualizacao"
]

STATUS_OPCOES = [
    "Agendado",
    "Aguardando portaria",
    "No pátio",
    "Em operação",
    "Finalizado",
    "Cancelado"
]


# =========================
# ESTILO
# =========================
st.markdown("""
<style>
    .stApp {
        background-color: #0b1220;
        color: white;
    }

    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-bottom: 0;
    }

    .sub-title {
        font-size: 15px;
        color: #c7cbd1;
        margin-top: 0;
        margin-bottom: 20px;
    }

    .parker-bar {
        height: 6px;
        width: 100%;
        background: linear-gradient(90deg, #ffcc00 0%, #f5b800 100%);
        border-radius: 8px;
        margin-bottom: 22px;
    }

    div[data-testid="stMetric"] {
        background-color: #121a2b;
        border: 1px solid rgba(255, 204, 0, 0.18);
        padding: 14px;
        border-radius: 12px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        background-color: #0f1726;
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        background-color: #121a2b;
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.12);
    }

    .stSelectbox > div > div,
    .stDateInput > div > div,
    .stTimeInput > div > div {
        background-color: #121a2b;
        border-radius: 10px;
    }

    .portal-note {
        color: #aeb6c2;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# FUNÇÕES
# =========================
def inicializar_arquivo():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        df_inicial = pd.DataFrame([
            {
                "id": str(uuid.uuid4())[:8],
                "placa": "ABC1D23",
                "transportadora": "Transportadora Exemplo",
                "tipo_operacao": "Recebimento",
                "doca": "Doca 01",
                "status": "Agendado",
                "nota_fiscal": "123456",
                "motorista": "João Silva",
                "data_agendada": datetime.now().strftime("%Y-%m-%d"),
                "hora_agendada": "08:00",
                "hora_entrada": "",
                "hora_saida": "",
                "observacoes": "Carga de teste",
                "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        ], columns=COLUNAS)

        df_inicial.to_csv(DATA_FILE, index=False)


def carregar_dados():
    inicializar_arquivo()

    try:
        df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    except Exception:
        df = pd.DataFrame(columns=COLUNAS)

    for col in COLUNAS:
        if col not in df.columns:
            df[col] = ""

    return df[COLUNAS].copy()


def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def badge_status(status):
    mapa = {
        "Agendado": "📅",
        "Aguardando portaria": "⏳",
        "No pátio": "🚛",
        "Em operação": "🏭",
        "Finalizado": "✅",
        "Cancelado": "❌"
    }
    return mapa.get(status, "📌")


# =========================
# HEADER
# =========================
header1, header2, header3 = st.columns([1, 5, 1.2])

with header1:
    if os.path.exists("assets/parker_logo.png"):
        st.image("assets/parker_logo.png", width=130)

with header2:
    st.markdown('<div class="main-title">Business System - YMS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Controle de janelas, recebimento, coletas e pátio</div>',
        unsafe_allow_html=True
    )

with header3:
    st.write("")
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.rerun()

st.markdown('<div class="parker-bar"></div>', unsafe_allow_html=True)


# =========================
# DADOS
# =========================
df = carregar_dados()

# =========================
# MÉTRICAS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros", len(df))
col2.metric("No pátio", len(df[df["status"] == "No pátio"]))
col3.metric("Em operação", len(df[df["status"] == "Em operação"]))
col4.metric("Finalizados", len(df[df["status"] == "Finalizado"]))

st.divider()

# =========================
# ABAS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Painel",
    "🗓️ Novo agendamento",
    "🚛 Operação / Status",
    "⬇️ Exportação"
])

# =========================
# TAB 1 - PAINEL
# =========================
with tab1:
    st.subheader("Visão geral da operação")

    filtro_status, filtro_tipo = st.columns(2)

    with filtro_status:
        status_selecionado = st.selectbox(
            "Filtrar por status",
            ["Todos"] + STATUS_OPCOES
        )

    with filtro_tipo:
        tipos = sorted([x for x in df["tipo_operacao"].dropna().unique() if x])
        tipo_selecionado = st.selectbox(
            "Filtrar por tipo de operação",
            ["Todos"] + tipos
        )

    busca = st.text_input("Pesquisar por placa, transportadora, NF ou motorista")

    painel_df = df.copy()

    if status_selecionado != "Todos":
        painel_df = painel_df[painel_df["status"] == status_selecionado]

    if tipo_selecionado != "Todos":
        painel_df = painel_df[painel_df["tipo_operacao"] == tipo_selecionado]

    if busca:
        painel_df = painel_df[
            painel_df["placa"].str.contains(busca, case=False, na=False) |
            painel_df["transportadora"].str.contains(busca, case=False, na=False) |
            painel_df["nota_fiscal"].str.contains(busca, case=False, na=False) |
            painel_df["motorista"].str.contains(busca, case=False, na=False)
        ]

    st.markdown(
        '<div class="portal-note">Aqui você acompanha o fluxo geral do pátio e das janelas de recebimento/coleta.</div>',
        unsafe_allow_html=True
    )

    exibir = painel_df.copy()
    exibir["status"] = exibir["status"].apply(lambda x: f"{badge_status(x)} {x}")

    st.dataframe(
        exibir[
            [
                "placa",
                "transportadora",
                "tipo_operacao",
                "doca",
                "status",
                "nota_fiscal",
                "motorista",
                "data_agendada",
                "hora_agendada",
                "hora_entrada",
                "hora_saida",
                "ultima_atualizacao"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# =========================
# TAB 2 - NOVO AGENDAMENTO
# =========================
with tab2:
    st.subheader("Cadastro de novo agendamento")

    with st.form("form_novo_agendamento"):
        c1, c2, c3 = st.columns(3)

        with c1:
            placa = st.text_input("Placa")
            transportadora = st.text_input("Transportadora")
            motorista = st.text_input("Motorista")

        with c2:
            tipo_operacao = st.selectbox("Tipo de operação", ["Recebimento", "Coleta", "Transferência"])
            doca = st.text_input("Doca")
            nota_fiscal = st.text_input("Nota fiscal")

        with c3:
            data_agendada = st.date_input("Data agendada")
            hora_agendada = st.time_input("Hora agendada")
            status_inicial = st.selectbox("Status inicial", ["Agendado", "Aguardando portaria"])

        observacoes = st.text_area("Observações")

        enviar = st.form_submit_button("Salvar agendamento")

        if enviar:
            if not placa.strip():
                st.error("Informe a placa.")
            else:
                novo = {
                    "id": str(uuid.uuid4())[:8],
                    "placa": placa.strip().upper(),
                    "transportadora": transportadora.strip(),
                    "tipo_operacao": tipo_operacao,
                    "doca": doca.strip(),
                    "status": status_inicial,
                    "nota_fiscal": nota_fiscal.strip(),
                    "motorista": motorista.strip(),
                    "data_agendada": str(data_agendada),
                    "hora_agendada": str(hora_agendada)[:5],
                    "hora_entrada": "",
                    "hora_saida": "",
                    "observacoes": observacoes.strip(),
                    "ultima_atualizacao": agora()
                }

                df_novo = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_novo)
                st.success("Agendamento salvo com sucesso.")
                st.rerun()

# =========================
# TAB 3 - OPERAÇÃO / STATUS
# =========================
with tab3:
    st.subheader("Atualização operacional")

    if df.empty:
        st.info("Nenhum registro disponível.")
    else:
        df_oper = df.copy()
        df_oper["descricao"] = (
            df_oper["placa"] + " | " +
            df_oper["transportadora"] + " | " +
            df_oper["status"] + " | " +
            df_oper["tipo_operacao"]
        )

        selecionado = st.selectbox(
            "Selecione o registro",
            df_oper["descricao"].tolist()
        )

        linha = df_oper[df_oper["descricao"] == selecionado].iloc[0]
        idx = linha.name

        with st.form("form_atualizacao"):
            c1, c2 = st.columns(2)

            with c1:
                novo_status = st.selectbox(
                    "Novo status",
                    STATUS_OPCOES,
                    index=STATUS_OPCOES.index(linha["status"]) if linha["status"] in STATUS_OPCOES else 0
                )
                nova_doca = st.text_input("Doca", value=linha["doca"])
                nova_nf = st.text_input("Nota fiscal", value=linha["nota_fiscal"])

            with c2:
                novo_motorista = st.text_input("Motorista", value=linha["motorista"])
                nova_transportadora = st.text_input("Transportadora", value=linha["transportadora"])
                nova_placa = st.text_input("Placa", value=linha["placa"])

            novas_obs = st.text_area("Observações", value=linha["observacoes"])

            atualizar = st.form_submit_button("Atualizar registro")

            if atualizar:
                df.at[idx, "placa"] = nova_placa.strip().upper()
                df.at[idx, "transportadora"] = nova_transportadora.strip()
                df.at[idx, "motorista"] = novo_motorista.strip()
                df.at[idx, "doca"] = nova_doca.strip()
                df.at[idx, "nota_fiscal"] = nova_nf.strip()
                df.at[idx, "observacoes"] = novas_obs.strip()
                df.at[idx, "status"] = novo_status
                df.at[idx, "ultima_atualizacao"] = agora()

                if novo_status == "No pátio" and not str(df.at[idx, "hora_entrada"]).strip():
                    df.at[idx, "hora_entrada"] = agora()

                if novo_status == "Finalizado" and not str(df.at[idx, "hora_saida"]).strip():
                    df.at[idx, "hora_saida"] = agora()

                salvar_dados(df)
                st.success("Registro atualizado com sucesso.")
                st.rerun()

        st.markdown("### Ações rápidas")
        a1, a2, a3 = st.columns(3)

        with a1:
            if st.button("🚛 Marcar entrada no pátio", use_container_width=True):
                df.at[idx, "status"] = "No pátio"
                if not str(df.at[idx, "hora_entrada"]).strip():
                    df.at[idx, "hora_entrada"] = agora()
                df.at[idx, "ultima_atualizacao"] = agora()
                salvar_dados(df)
                st.success("Entrada no pátio registrada.")
                st.rerun()

        with a2:
            if st.button("🏭 Marcar em operação", use_container_width=True):
                df.at[idx, "status"] = "Em operação"
                df.at[idx, "ultima_atualizacao"] = agora()
                salvar_dados(df)
                st.success("Registro marcado como em operação.")
                st.rerun()

        with a3:
            if st.button("✅ Finalizar", use_container_width=True):
                df.at[idx, "status"] = "Finalizado"
                if not str(df.at[idx, "hora_saida"]).strip():
                    df.at[idx, "hora_saida"] = agora()
                df.at[idx, "ultima_atualizacao"] = agora()
                salvar_dados(df)
                st.success("Operação finalizada.")
                st.rerun()

# =========================
# TAB 4 - EXPORTAÇÃO
# =========================
with tab4:
    st.subheader("Exportação e apoio")

    st.download_button(
        label="⬇️ Baixar base atual em CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="yms_operacao_export.csv",
        mime="text/csv"
    )

    st.warning(
        "Este modelo é ótimo para estruturação e testes. Para uso real com múltiplos usuários, "
        "o ideal é conectar um banco de dados corporativo com apoio do TI."
    )
