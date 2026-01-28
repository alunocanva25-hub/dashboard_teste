import streamlit as st
import pandas as pd
import plotly.express as px
import requests, re
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import streamlit.components.v1 as components
from datetime import date

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(page_title="Dashboard Notas – AM x AS", layout="wide")

# ======================================================
# CSS (visual do dashboard + organização)
# ======================================================
st.markdown("""
<style>
.stApp { background: #6fa6d6; }
.block-container{ padding-top: 0.6rem; max-width: 1500px; }

/* ======================================================
   LOGIN (apenas quando .login-mode estiver ativo)
   ====================================================== */
.stApp.login-mode .block-container{
  max-width: 980px !important;
  padding-top: 20px !important;
}
.stApp.login-mode header, 
.stApp.login-mode footer, 
.stApp.login-mode [data-testid="stSidebar"], 
.stApp.login-mode [data-testid="stToolbar"]{
  display:none !important;
}

/* container central */
.login-shell{
  display:flex;
  justify-content:center;
  align-items:flex-start;
  padding: 12px 0 0 0;
}
.login-card{
  width: min(980px, 94vw);
  border-radius: 26px;
  overflow: hidden;
  box-shadow: 0 16px 28px rgba(0,0,0,0.28);
  border: 2px solid rgba(10,40,70,0.20);
}

/* topo */
.login-head{
  padding: 22px 26px 18px 26px;
  background: #2f6f8c;
}
.login-title{
  display:flex; align-items:center; gap:12px;
  font-weight: 950;
  color:#ffffff;
  font-size: 34px;
  line-height: 1;
}
.login-sub{
  margin-top: 8px;
  color: rgba(255,255,255,0.92);
  font-weight: 800;
  font-size: 16px;
}

/* faixa clara abaixo do topo */
.login-band{
  height: 46px;
  background: rgba(255,255,255,0.35);
}

/* corpo */
.login-body{
  padding: 26px 22px 10px 22px;
  background: transparent;
}

/* Inputs do Streamlit (somente em login-mode) */
.stApp.login-mode div[data-testid="stTextInput"]{
  margin-bottom: 10px;
}
.stApp.login-mode div[data-testid="stTextInput"] input{
  height: 44px !important;
  border-radius: 10px !important;
  background: #15181c !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  color: #ffffff !important;
  font-weight: 900 !important;
  font-size: 16px !important;
}
.stApp.login-mode div[data-testid="stTextInput"] input::placeholder{
  color: rgba(255,255,255,0.45) !important;
  font-weight: 800 !important;
}

/* alinha o "olhinho" do password com o campo */
.stApp.login-mode div[data-testid="stTextInput"] svg{
  color: rgba(255,255,255,0.75) !important;
}

/* Botões do login */
.stApp.login-mode div.stButton > button{
  border-radius: 10px !important;
  font-weight: 900 !important;
  border: 2px solid rgba(10,40,70,0.22) !important;
  background: rgba(255,255,255,0.55) !important;
  color:#0b2b45 !important;
  padding: .30rem .90rem !important;
}
.stApp.login-mode div.stButton > button:hover{
  background: rgba(255,255,255,0.75) !important;
  border-color: rgba(10,40,70,0.35) !important;
}

/* rodapé do login */
.login-foot{
  text-align:center;
  padding: 10px 0 16px 0;
  font-weight: 900;
  color: rgba(11,43,69,0.92);
  font-size: 12px;
}
.login-foot .ok{
  display:inline-flex; align-items:center; gap:8px;
}
.login-foot .dot{
  width: 12px; height: 12px;
  border-radius: 3px;
  background: #2e7d32;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.35) inset;
}

/* ======================================================
   DASHBOARD (o que já existia)
   ====================================================== */
.card{
  background: #b9d3ee;
  border: 2px solid rgba(10,40,70,0.30);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 10px 18px rgba(0,0,0,0.18);
  margin-bottom: 14px;
  text-align: center;
}
.card-title{
  font-weight: 950;
  color:#0b2b45;
  font-size: 13px;
  text-transform: uppercase;
  margin-bottom: 10px;
  letter-spacing: .3px;
  text-align: center;
}

.kpi-row{
  display:flex;
  justify-content:space-between;
  align-items:flex-end;
  gap: 10px;
}
.kpi-big{
  font-size: 42px;
  font-weight: 950;
  color:#9b0d0d;
  line-height: 1.0;
}
.kpi-mini{
  text-align:center;
}
.kpi-mini .lbl{
  font-weight:900; color:#0b2b45; font-size:12px; text-transform:uppercase;
}
.kpi-mini .val{
  font-weight:950; color:#9b0d0d; font-size:26px; line-height: 1.0;
}

.topbar{
  background: rgba(255,255,255,0.35);
  border: 2px solid rgba(10,40,70,0.22);
  border-radius: 18px;
  padding: 10px 14px;
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom: 10px;
}
.brand{
  display:flex; align-items:center; gap:12px;
}
.brand-badge{
  width:46px; height:46px; border-radius: 14px;
  background: rgba(255,255,255,0.55);
  border: 2px solid rgba(10,40,70,0.22);
  display:flex; align-items:center; justify-content:center;
  font-weight: 950; color:#0b2b45;
}
.brand-text .t1{ font-weight:950; color:#0b2b45; line-height:1.1; }
.brand-text .t2{ font-weight:800; color:#0b2b45; opacity:.85; font-size:12px; }

.right-note{
  text-align:right; font-weight:950; color:#0b2b45;
}
.right-note small{ font-weight:800; opacity:.9; font-size:12px; }

div.stButton > button{
  border-radius: 10px;
  font-weight: 900;
  border: 2px solid rgba(10,40,70,0.22);
  background: rgba(255,255,255,0.45);
  color:#0b2b45;
  padding: .25rem .6rem;
}
div.stButton > button:hover{
  background: rgba(255,255,255,0.65);
  border-color: rgba(10,40,70,0.35);
}

/* Segmented control (aba ativa com cor diferente) */
div[data-baseweb="segmented-control"]{
  background: rgba(255,255,255,0.35);
  border: 2px solid rgba(10,40,70,0.22);
  border-radius: 14px;
  padding: 6px;
}
div[data-baseweb="segmented-control"] span{
  font-weight: 900 !important;
  color: #0b2b45 !important;
}
div[data-baseweb="segmented-control"] div[aria-checked="true"]{
  background: #0b2b45 !important;
  border-radius: 10px !important;
}
div[data-baseweb="segmented-control"] div[aria-checked="true"] span{
  color: #ffffff !important;
}

/* Lista (notas por localidade) */
.loc-row{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:6px 8px;
  border-radius:10px;
  margin-bottom:6px;
  border:1px solid rgba(10,40,70,0.22);
  background: rgba(255,255,255,0.35);
  color:#0b2b45;
  font-weight: 900;
}
.loc-row.active{
  background:#0b2b45;
  color:#ffffff;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOGIN (ALTERADO para ficar igual ao da imagem)
# ======================================================
def _set_login_mode(on: bool):
    # adiciona/remove a classe no DOM do Streamlit (para scoping do CSS)
    if on:
        components.html("""
        <script>
          const app = window.parent.document.querySelector('.stApp');
          if (app) app.classList.add('login-mode');
        </script>
        """, height=0)
    else:
        components.html("""
        <script>
          const app = window.parent.document.querySelector('.stApp');
          if (app) app.classList.remove('login-mode');
        </script>
        """, height=0)

def tela_login():
    _set_login_mode(True)

    # cabeçalho igual ao layout da imagem
    st.markdown("""
    <div class="login-shell">
      <div class="login-card">
        <div class="login-head">
          <div class="login-title">🔐&nbsp;Acesso Restrito</div>
          <div class="login-sub">Torpedo Semanal • Produtividade</div>
        </div>
        <div class="login-band"></div>
        <div class="login-body">
    """, unsafe_allow_html=True)

    # inputs (labels colapsadas + placeholder)
    usuario = st.text_input(
        label="Usuário",
        placeholder="Digite seu usuário",
        key="login_user",
        label_visibility="collapsed",
    )
    senha = st.text_input(
        label="Senha",
        placeholder="Digite sua senha",
        type="password",
        key="login_pass",
        label_visibility="collapsed",
    )

    c1, c2, c3 = st.columns([1, 1, 6])
    with c1:
        entrar = st.button("Entrar", key="btn_entrar")
    with c2:
        limpar = st.button("Limpar", key="btn_limpar")

    if limpar:
        st.session_state["login_user"] = ""
        st.session_state["login_pass"] = ""
        st.rerun()

    if entrar:
        if usuario == st.secrets["auth"]["usuario"] and senha == st.secrets["auth"]["senha"]:
            st.session_state["logado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.markdown("""
        </div>
        <div class="login-foot">
          <span class="ok"><span class="dot"></span>Segurança via st.secrets</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    tela_login()
    st.stop()
else:
    _set_login_mode(False)

# ======================================================
# TOPO
# ======================================================
st.markdown("""
<div class="topbar">
  <div class="brand">
    <div class="brand-badge">3C</div>
    <div class="brand-text">
      <div class="t1">DASHBOARD NOTAS – AM x AS</div>
      <div class="t2">Visão gerencial no padrão do painel de referência</div>
    </div>
  </div>
  <div class="right-note">
    FUNÇÃO MEDIÇÃO<br>
    <small>NOTAS AM – ANÁLISE DE MEDIÇÃO<br>NOTAS AS – AUDITORIA DE SERVIÇO</small>
  </div>
</div>
""", unsafe_allow_html=True)

# ======================================================
# CONSTANTES / CORES
# ======================================================
MESES_PT = {
    1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL",
    5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO",
    9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
}
MESES_ORDEM = [MESES_PT[i] for i in range(1, 13)]

COR_PROC = "#2e7d32"
COR_IMP  = "#c62828"
COR_OUT  = "#546e7a"
COR_TOT  = "#fcba03"

# ======================================================
# HELPERS (colunas / validação)
# ======================================================
def achar_coluna(df, palavras):
    for col in df.columns:
        for p in palavras:
            if p in col:
                return col
    return None

def validar_estrutura(df):
    obrig = {
        "ESTADO/UF": ["ESTADO", "LOCALIDADE", "UF"],
        "RESULTADO": ["RESULTADO"],
        "TIPO": ["TIPO"],
        "DATA": ["DATA"],
    }
    faltando = [nome for nome, alts in obrig.items() if not achar_coluna(df, alts)]
    if faltando:
        st.error("Estrutura da base incompatível. Faltando: " + ", ".join(faltando))
        st.stop()

def _extrair_drive_id(url: str):
    m = re.search(r"[?&]id=([a-zA-Z0-9-_]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/file/d/([a-zA-Z0-9-_]+)", url)
    if m:
        return m.group(1)
    return None

def _drive_direct_download(url: str) -> str:
    did = _extrair_drive_id(url)
    if did:
        return f"https://drive.google.com/uc?id={did}"
    return url

def _bytes_is_html(raw: bytes) -> bool:
    head = raw[:800].lstrip().lower()
    return head.startswith(b"<!doctype html") or b"<html" in head

def _bytes_is_xlsx(raw: bytes) -> bool:
    return raw[:2] == b"PK"

@st.cache_data(ttl=600, show_spinner="🔄 Carregando base (XLSX/CSV)...")
def carregar_base(url_original: str) -> pd.DataFrame:
    url = _drive_direct_download(url_original)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    raw = r.content

    if _bytes_is_html(raw):
        raise RuntimeError("URL retornou HTML (provável permissão/link). No Drive: 'Qualquer pessoa com o link' (Visualizador).")

    if _bytes_is_xlsx(raw):
        df = pd.read_excel(BytesIO(raw), sheet_name=0, engine="openpyxl")
        df.columns = df.columns.astype(str).str.upper().str.strip()
        return df

    for enc in ["utf-8-sig", "utf-8", "cp1252", "latin1"]:
        try:
            df = pd.read_csv(BytesIO(raw), sep=None, engine="python", encoding=enc)
            df.columns = df.columns.astype(str).str.upper().str.strip()
            return df
        except UnicodeDecodeError:
            continue

    df = pd.read_csv(BytesIO(raw), sep=None, engine="python", encoding="utf-8", encoding_errors="replace")
    df.columns = df.columns.astype(str).str.upper().str.strip()
    return df

def _titulo_plotly(fig, titulo: str, uf: str):
    uf_txt = uf if uf != "TOTAL" else "TODOS"
    fig.update_layout(
        title=f"{titulo} • {uf_txt}",
        title_x=0.0,
        title_font=dict(size=14, color="#FFFFFF", family="Arial Black")
    )
    return fig

# ======================================================
# GRÁFICOS AUXILIARES
# ======================================================
def donut_resultado(df_base):
    proc = df_base["_RES_"].str.contains("PROCED", na=False).sum()
    imp  = df_base["_RES_"].str.contains("IMPROCED", na=False).sum()
    dados = pd.DataFrame({"Resultado": ["Procedente", "Improcedente"], "QTD": [proc, imp]})
    fig = px.pie(
        dados, names="Resultado", values="QTD", hole=0.62,
        template="plotly_white",
        color="Resultado",
        color_discrete_map={"Procedente": COR_PROC, "Improcedente": COR_IMP}
    )
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=60, b=10), legend_title_text="")
    fig.update_traces(textinfo="percent+value")
    return fig

def barh_contagem(df_base, col_dim, titulo, uf):
    if col_dim is None or df_base.empty:
        return None

    dados = (
        df_base
        .groupby(col_dim)
        .size()
        .reset_index(name="QTD")
        .sort_values("QTD")
    )

    if dados.empty:
        return None

    total = int(dados["QTD"].sum())
    total_fmt = f"{total:,}".replace(",", ".")

    fig = px.bar(
        dados,
        x="QTD",
        y=col_dim,
        orientation="h",
        text="QTD",
        template="plotly_white"
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=70, b=10),
        showlegend=False,
    )

    fig.update_xaxes(visible=False, showticklabels=False, ticks="", showgrid=False, zeroline=False)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(title_text="")

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=1.12,
        text=f"TOTAL: {total_fmt}",
        showarrow=False,
        font=dict(size=13, color=COR_TOT, family="Arial Black"),
        align="right"
    )

    return _titulo_plotly(fig, titulo, uf)

# ======================================================
# ACUMULADO MENSAL (gráfico + tabelinha + bloquinhos + total direito)
# ======================================================
def acumulado_mensal_fig_e_tabela(df_base, col_data):
    base = df_base.dropna(subset=[col_data]).copy()
    if base.empty:
        return None, None

    base["MES_NUM"] = base[col_data].dt.month
    base["MÊS"] = base["MES_NUM"].map(MESES_PT)

    base["_CLASSE_"] = "OUTROS"
    base.loc[base["_RES_"].str.contains("PROCED", na=False), "_CLASSE_"] = "PROCEDENTE"
    base.loc[base["_RES_"].str.contains("IMPROCED", na=False), "_CLASSE_"] = "IMPROCEDENTE"

    classes = ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"]

    dados_raw = (
        base.groupby(["MES_NUM", "MÊS", "_CLASSE_"])
        .size()
        .reset_index(name="QTD")
    )

    meses_df = pd.DataFrame({"MES_NUM": list(range(1, 13))})
    meses_df["MÊS"] = meses_df["MES_NUM"].map(MESES_PT)

    grid = (
        meses_df.assign(_k=1)
        .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
        .drop(columns="_k")
    )

    dados = (
        grid.merge(dados_raw, on=["MES_NUM", "MÊS", "_CLASSE_"], how="left")
        .fillna({"QTD": 0})
    )
    dados["QTD"] = dados["QTD"].astype(int)

    total_mes = dados.groupby("MES_NUM")["QTD"].transform("sum")
    denom = total_mes.replace(0, 1)
    dados["PCT"] = ((dados["QTD"] / denom) * 100).round(0).astype(int)

    dados["LABEL"] = ""
    mask_p = dados["_CLASSE_"] == "PROCEDENTE"
    mask_i = dados["_CLASSE_"] == "IMPROCEDENTE"
    dados.loc[mask_p, "LABEL"] = dados.loc[mask_p, "PCT"].astype(str) + "%"
    dados.loc[mask_i, "LABEL"] = dados.loc[mask_i, "PCT"].astype(str) + "%"

    tab = (
        dados.pivot_table(
            index=["MES_NUM", "MÊS"],
            columns="_CLASSE_",
            values="QTD",
            aggfunc="sum",
            fill_value=0
        )
        .reset_index()
        .sort_values("MES_NUM")
    )

    for c in classes:
        if c not in tab.columns:
            tab[c] = 0

    tab["TOTAL"] = tab["PROCEDENTE"] + tab["IMPROCEDENTE"] + tab["OUTROS"]
    tabela_final = tab[["MÊS", "IMPROCEDENTE", "PROCEDENTE", "TOTAL"]].copy()

    fig = px.bar(
        dados.sort_values("MES_NUM"),
        x="MÊS",
        y="QTD",
        color="_CLASSE_",
        barmode="stack",
        text="LABEL",
        category_orders={
            "MÊS": MESES_ORDEM,
            "_CLASSE_": ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"],
        },
        color_discrete_map={
            "PROCEDENTE": COR_PROC,
            "IMPROCEDENTE": COR_IMP,
            "OUTROS": COR_OUT,
        },
        template="plotly_dark",
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(visible=False, showgrid=False, zeroline=False, showticklabels=False, title_text="")

    fig.update_layout(
        height=520,
        showlegend=False,
        margin=dict(l=120, r=170, t=50, b=190),
        xaxis_title="",
        yaxis_title="",
    )

    def _fmt_int(v: int) -> str:
        return f"{int(v):,}".replace(",", ".")

    y_base = -0.23
    dy = 0.055

    line_style = dict(color="rgba(255,255,255,0.25)", width=1)
    for k in range(3):
        y_line = y_base - (k * dy)
        fig.add_shape(
            type="line", xref="paper", yref="paper",
            x0=0, x1=1, y0=y_line, y1=y_line,
            line=line_style
        )

    for _, r in tab.iterrows():
        mes = r["MÊS"]
        p = _fmt_int(r["PROCEDENTE"])
        i = _fmt_int(r["IMPROCEDENTE"])
        t = _fmt_int(r["TOTAL"])

        fig.add_annotation(
            x=mes, xref="x",
            yref="paper", y=y_base,
            text=f"<span style='font-family:monospace;font-size:14px;color:{COR_PROC};'><b>{p}</b></span>",
            showarrow=False, align="center",
        )
        fig.add_annotation(
            x=mes, xref="x",
            yref="paper", y=y_base - dy,
            text=f"<span style='font-family:monospace;font-size:14px;color:{COR_IMP};'><b>{i}</b></span>",
            showarrow=False, align="center",
        )
        fig.add_annotation(
            x=mes, xref="x",
            yref="paper", y=y_base - (2 * dy),
            text=f"<span style='font-family:monospace;font-size:14px;color:{COR_TOT};'><b>{t}</b></span>",
            showarrow=False, align="center",
        )

    x_leg = -0.08
    y_leg = y_base

    fig.add_annotation(
        xref="paper", yref="paper",
        x=x_leg, y=y_leg,
        text=(f"<span style='color:{COR_PROC};font-size:16px'>■</span> "
              "<span style='color:white;font-size:14px'><b>PROCEDENTE</b></span>"),
        showarrow=False, align="left",
    )
    fig.add_annotation(
        xref="paper", yref="paper",
        x=x_leg, y=y_leg - dy,
        text=(f"<span style='color:{COR_IMP};font-size:16px'>■</span> "
              "<span style='color:white;font-size:14px'><b>IMPROCEDENTE</b></span>"),
        showarrow=False, align="left",
    )
    fig.add_annotation(
        xref="paper", yref="paper",
        x=x_leg, y=y_leg - (2 * dy),
        text=("<span style='color:#fcba03;font-size:16px'>■</span> "
              "<span style='color:white;font-size:14px'><b>TOTAL</b></span>"),
        showarrow=False, align="left",
    )

    total_geral = int(tab["TOTAL"].sum())
    total_proc  = int(tab["PROCEDENTE"].sum())
    total_imp   = int(tab["IMPROCEDENTE"].sum())

    total_geral_fmt = f"{total_geral:,}".replace(",", ".")
    total_proc_fmt  = f"{total_proc:,}".replace(",", ".")
    total_imp_fmt   = f"{total_imp:,}".replace(",", ".")

    fig.add_annotation(
        xref="paper", yref="paper",
        x=1.10, y=0.55,
        text=(
            "<span style='font-size:12px;color:#fcba03'><b>TOTAL</b></span><br>"
            f"<span style='font-size:18px;color:#fcba03'><b>{total_geral_fmt}</b></span><br><br>"
            f"<span style='font-size:12px;color:{COR_PROC}'><b>PROCEDENTE</b></span><br>"
            f"<span style='font-size:16px;color:{COR_PROC}'><b>{total_proc_fmt}</b></span><br><br>"
            f"<span style='font-size:12px;color:{COR_IMP}'><b>IMPROCEDENTE</b></span><br>"
            f"<span style='font-size:16px;color:{COR_IMP}'><b>{total_imp_fmt}</b></span>"
        ),
        showarrow=False,
        align="left",
        bgcolor="rgba(0,0,0,0.45)",
        bordercolor="#fcba03",
        borderwidth=1,
        borderpad=10,
    )

    return fig, tabela_final

# ======================================================
# HTML (Notas por localidade)
# ======================================================
def resumo_por_localidade_html(df_base, col_local, selecionado, top_n=12):
    if col_local is None or df_base.empty:
        return ""
    s = df_base[col_local].dropna().astype(str).str.upper()
    vc = s.value_counts().reset_index()
    vc.columns = ["LOCAL", "QTD"]
    if len(vc) > top_n:
        outros = int(vc.iloc[top_n:]["QTD"].sum())
        vc = vc.iloc[:top_n].copy()
        vc.loc[len(vc)] = ["OUTROS", outros]
    linhas = []
    sel = str(selecionado).upper()
    for _, r in vc.iterrows():
        loc = r["LOCAL"]
        qtd = int(r["QTD"])
        active = (sel != "TOTAL" and loc == sel)
        cls = "loc-row active" if active else "loc-row"
        qtd_fmt = f"{qtd:,}".replace(",", ".")
        linhas.append(f'<div class="{cls}"><span>{loc}</span><span>{qtd_fmt}</span></div>')
    return "\n".join(linhas)

# ======================================================
# BOTÃO ATUALIZAR BASE
# ======================================================
colA, colB = st.columns([1, 6])
with colA:
    if st.button("🔄 Atualizar base"):
        st.cache_data.clear()
        st.rerun()
with colB:
    st.caption("Use quando atualizar o arquivo no Drive (XLSX).")

# ======================================================
# CARREGAMENTO (XLSX no Drive)
# ======================================================
URL_BASE = "https://drive.google.com/uc?id=1VadynN01W4mNRLfq8ABZAaQP8Sfim5tb"

df = carregar_base(URL_BASE)
validar_estrutura(df)

COL_ESTADO    = achar_coluna(df, ["ESTADO", "LOCALIDADE", "UF"])
COL_RESULTADO = achar_coluna(df, ["RESULTADO"])
COL_TIPO      = achar_coluna(df, ["TIPO"])
COL_MOTIVO    = achar_coluna(df, ["MOTIVO"])
COL_REGIONAL  = achar_coluna(df, ["REGIONAL"])
COL_DATA      = achar_coluna(df, ["DATA"])

df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)
df["_TIPO_"] = df[COL_TIPO].astype(str).str.upper().str.strip()
df["_RES_"]  = df[COL_RESULTADO].astype(str).str.upper().str.strip()

# ======================================================
# SELETORES (Ano • Mensal/Semanal • Calendário • Semana)
# ======================================================
anos_disponiveis = sorted(df[COL_DATA].dropna().dt.year.unique().astype(int).tolist())
ano_padrao = anos_disponiveis[-1] if anos_disponiveis else None

c_sel1, c_sel2, c_sel3, c_sel4 = st.columns([1.0, 1.3, 2.2, 2.0], gap="medium")

with c_sel1:
    ano_sel = st.selectbox(
        "Ano",
        options=anos_disponiveis if anos_disponiveis else ["—"],
        index=(len(anos_disponiveis) - 1) if anos_disponiveis else 0,
        key="ano_sel",
    )
    if ano_sel == "—":
        ano_sel = None

with c_sel2:
    modo_periodo = st.segmented_control(
        "Período",
        options=["Mensal", "Semanal"],
        default=st.session_state.get("modo_periodo", "Mensal"),
        key="modo_periodo",
    )

df_ano = df if ano_sel is None else df[df[COL_DATA].dt.year == int(ano_sel)].copy()
ano_txt = str(ano_sel) if ano_sel else "—"

if not df_ano.empty and df_ano[COL_DATA].notna().any():
    _min_d = df_ano[COL_DATA].min().date()
    _max_d = df_ano[COL_DATA].max().date()
else:
    _min_d = date.today()
    _max_d = date.today()

with c_sel3:
    data_ini, data_fim = st.date_input(
        "Filtro por calendário (início/fim)",
        value=(st.session_state.get("data_ini", _min_d), st.session_state.get("data_fim", _max_d)),
        min_value=_min_d,
        max_value=_max_d,
        key="range_calendario",
    )

with c_sel4:
    semana_sel = None
    if modo_periodo == "Semanal" and not df_ano.empty:
        semanas_disp = sorted(df_ano[COL_DATA].dropna().dt.isocalendar().week.unique().astype(int).tolist())
        opcoes_sem = ["Todas"] + [f"S{w:02d}" for w in semanas_disp]
        semana_sel = st.selectbox("Semana (S01..S53)", opcoes_sem, index=0, key="semana_sel")

if modo_periodo == "Semanal" and semana_sel and semana_sel != "Todas" and ano_sel is not None:
    w = int(str(semana_sel).replace("S", ""))
    try:
        data_ini = date.fromisocalendar(int(ano_sel), w, 1)
        data_fim = date.fromisocalendar(int(ano_sel), w, 5)
        st.caption(f"Semana {semana_sel}: {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} (seg–sex)")
    except ValueError:
        st.warning("Semana inválida para este ano (ISO). Usando o filtro por calendário.")

df_periodo = df_ano.copy()
if not df_periodo.empty and df_periodo[COL_DATA].notna().any():
    _dini = pd.to_datetime(data_ini)
    _dfim = pd.to_datetime(data_fim) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    df_periodo = df_periodo[(df_periodo[COL_DATA] >= _dini) & (df_periodo[COL_DATA] <= _dfim)].copy()

# ======================================================
# "ABAS" UF
# ======================================================
ufs = sorted(df[COL_ESTADO].dropna().astype(str).str.upper().unique().tolist())
ufs = ["TOTAL"] + ufs
if "uf_sel" not in st.session_state:
    st.session_state.uf_sel = "TOTAL"
uf_sel = st.segmented_control(label="", options=ufs, default=st.session_state.uf_sel)
st.session_state.uf_sel = uf_sel

df_filtro = df_periodo if uf_sel == "TOTAL" else df_periodo[df_periodo[COL_ESTADO].astype(str).str.upper() == uf_sel]
df_am = df_filtro[df_filtro["_TIPO_"].str.contains("AM", na=False)]
df_as = df_filtro[df_filtro["_TIPO_"].str.contains("AS", na=False)]

# ======================================================
# 6 BLOCOS (CARDS)
# ======================================================
row1 = st.columns([1.09, 1.15, 1.15], gap="large")

with row1[0]:
    total = len(df_filtro); am = len(df_am); az = len(df_as)
    total_fmt = f"{total:,}".replace(",", ".")
    am_fmt    = f"{am:,}".replace(",", ".")
    as_fmt    = f"{az:,}".replace(",", ".")
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">ACUMULADO DE NOTAS AM / AS • {ano_txt}</div>
          <div class="kpi-row">
            <div class="kpi-big">{total_fmt}</div>
            <div class="kpi-mini">
              <div class="lbl">AM</div>
              <div class="val">{am_fmt}</div>
            </div>
            <div class="kpi-mini">
              <div class="lbl">AS</div>
              <div class="val">{as_fmt}</div>
            </div>
          </div>
          <div style="margin-top:14px; text-align:left;">
            <div style="font-weight:950;color:#0b2b45;margin-bottom:8px;text-transform:uppercase;">
              Notas por localidade
            </div>
            {resumo_por_localidade_html(df_periodo, COL_ESTADO, uf_sel, top_n=12)}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with row1[1]:
    st.markdown('<div class="card"><div class="card-title">ACUMULADO ANUAL – AM</div>', unsafe_allow_html=True)
    if df_am.empty:
        st.info("Sem dados AM.")
    else:
        fig = donut_resultado(df_am)
        fig = _titulo_plotly(fig, "ACUMULADO ANUAL – AM", uf_sel)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with row1[2]:
    st.markdown('<div class="card"><div class="card-title">ACUMULADO ANUAL – AS</div>', unsafe_allow_html=True)
    if df_as.empty:
        st.info("Sem dados AS.")
    else:
        fig = donut_resultado(df_as)
        fig = _titulo_plotly(fig, "ACUMULADO ANUAL – AS", uf_sel)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

row2 = st.columns([1, 1.3, 1.3], gap="large")

with row2[0]:
    st.markdown('<div class="card"><div class="card-title">IMPROCEDÊNCIAS POR REGIONAL – NOTA AM</div>', unsafe_allow_html=True)
    base_imp_am = df_am[df_am["_RES_"].str.contains("IMPROCED", na=False)]
    fig = barh_contagem(base_imp_am, COL_REGIONAL, "IMPROCEDÊNCIAS POR REGIONAL – NOTA AM", uf_sel)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem improcedências (AM) por regional.")
    st.markdown("</div>", unsafe_allow_html=True)

with row2[1]:
    st.markdown('<div class="card"><div class="card-title">MOTIVOS DE IMPROCEDÊNCIAS – NOTA AM</div>', unsafe_allow_html=True)
    base_imp_am = df_am[df_am["_RES_"].str.contains("IMPROCED", na=False)]
    fig = barh_contagem(base_imp_am, COL_MOTIVO, "MOTIVOS DE IMPROCEDÊNCIAS – NOTA AM", uf_sel)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem motivos (AM).")
    st.markdown("</div>", unsafe_allow_html=True)

with row2[2]:
    st.markdown('<div class="card"><div class="card-title">MOTIVOS DE IMPROCEDÊNCIAS – NOTA AS</div>', unsafe_allow_html=True)
    base_imp_as = df_as[df_as["_RES_"].str.contains("IMPROCED", na=False)]
    fig = barh_contagem(base_imp_as, COL_MOTIVO, "MOTIVOS DE IMPROCEDÊNCIAS – NOTA AS", uf_sel)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem motivos (AS).")
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# ACUMULADO MENSAL
# ======================================================
st.markdown('<div class="card"><div class="card-title">ACUMULADO MENSAL DE NOTAS AM – AS</div>', unsafe_allow_html=True)

fig_mensal, tabela_mensal = acumulado_mensal_fig_e_tabela(df_filtro, COL_DATA)

if fig_mensal is not None:
    fig_mensal = _titulo_plotly(fig_mensal, "ACUMULADO MENSAL DE NOTAS AM – AS", uf_sel)
    st.plotly_chart(fig_mensal, use_container_width=True)
else:
    st.info("Sem dados mensais (DATA vazia/ inválida).")

st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# TABELA NO FINAL
# ======================================================
st.markdown('<div class="card"><div class="card-title">TABELA — VALORES MENSAIS</div>', unsafe_allow_html=True)
if tabela_mensal is not None:
    st.dataframe(tabela_mensal, use_container_width=True, hide_index=True)
else:
    st.info("Sem tabela mensal para exibir.")
st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# PDF (relatório)
# ======================================================
def gerar_pdf(df_tabela, ano_ref, uf_sel, df_filtro_ref, df_am_ref, df_as_ref):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elementos = []
    elementos.append(Paragraph(f"<b>DASHBOARD NOTAS AM x AS – {ano_ref}</b>", styles["Title"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"<b>UF selecionada:</b> {uf_sel}", styles["Normal"]))
    elementos.append(Spacer(1, 12))

    total = len(df_filtro_ref); am = len(df_am_ref); az = len(df_as_ref)
    elementos.append(Paragraph(
        f"<b>Total de Notas:</b> {total}<br/>"
        f"<b>AM:</b> {am} &nbsp;&nbsp; <b>AS:</b> {az}",
        styles["Normal"]
    ))
    elementos.append(Spacer(1, 14))

    if df_tabela is not None and not df_tabela.empty:
        data = [df_tabela.columns.tolist()] + df_tabela.values.tolist()
        tabela = Table(data, repeatRows=1)
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0,0), (-1,0), 8),
            ("TOPPADDING", (0,0), (-1,0), 8),
        ]))
        elementos.append(Paragraph("<b>Resumo Mensal</b>", styles["Heading2"]))
        elementos.append(Spacer(1, 8))
        elementos.append(tabela)

    doc.build(elementos)
    buffer.seek(0)
    return buffer

pdf_buffer = gerar_pdf(
    df_tabela=tabela_mensal,
    ano_ref=ano_txt,
    uf_sel=uf_sel,
    df_filtro_ref=df_filtro,
    df_am_ref=df_am,
    df_as_ref=df_as,
)

st.download_button(
    label="📄 Exportar PDF",
    data=pdf_buffer,
    file_name=f"IW58_Dashboard_{ano_txt}_{uf_sel}.pdf",
    mime="application/pdf"
)

# ======================================================
# RELATÓRIOS GERENCIAIS (COMPLETO)
# - Legendas padronizadas (embaixo) em TODOS os gráficos
# - Quadro (Procedente/Improcedente/Outros/Total) em TODOS os 3 relatórios
# - Comparativo Anual com % alinhada corretamente (sem bagunça)
# ======================================================

def _col_ok(c):
    return c is not None and str(c).strip() != ""

def _norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.upper().str.strip()

def _fmt_int(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")

def _classificar(df_):
    """
    ✅ CORREÇÃO: 'IMPROCEDENTE' contém 'PROCED'
    -> PROCEDENTE = contém 'PROCED' e NÃO contém 'IMPROCED'
    """
    d = df_.copy()
    if "_RES_" not in d.columns:
        d["_RES_"] = ""
    res = _norm(d["_RES_"].fillna(""))

    mask_improc = res.str.contains("IMPROCED", na=False)
    mask_proc = res.str.contains("PROCED", na=False) & (~mask_improc)

    d["_CLASSE_"] = "OUTROS"
    d.loc[mask_proc, "_CLASSE_"] = "PROCEDENTE"
    d.loc[mask_improc, "_CLASSE_"] = "IMPROCEDENTE"
    return d

def _style_clean(fig):
    fig.update_xaxes(showgrid=False, ticks="")
    fig.update_yaxes(showgrid=False, visible=False, showticklabels=False, ticks="", zeroline=False, title_text="")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    return fig

def _legend_bottom(fig, y=-0.22, font_size=12):
    """
    ✅ legenda horizontal embaixo do gráfico
    - y mais negativo = desce mais a legenda
    """
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=y,
            xanchor="left",
            x=0.0,
            title_text="",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=font_size, color="white"),
        )
    )
    return fig

def _add_summary_box(fig, proc, improc, outros, total, box_x=1.18, box_y=0.98):
    """
    ✅ Quadro de totais (Procedente/Improcedente/Outros/Total) DENTRO da FIGURA.

    COMO MOVER:
    - box_x (direita/esquerda):
        * aumenta box_x (ex.: 1.25) -> vai MAIS para a DIREITA
        * diminui box_x (ex.: 1.05) -> vai MAIS para a ESQUERDA
        * use 0.98 se quiser "dentro do plot" (canto superior direito)
        * use >1.00 para ficar na lateral (fora do plot, mas dentro da figura)
    - box_y (cima/baixo):
        * aumenta box_y (ex.: 1.02) -> sobe
        * diminui box_y (ex.: 0.90) -> desce
    """
    txt = (
        f"<span style='color:{COR_PROC};font-size:14px'>■</span> <b>PROCEDENTE</b><br>"
        f"<span style='color:{COR_PROC};font-size:18px'><b>{_fmt_int(proc)}</b></span><br><br>"
        f"<span style='color:{COR_IMP};font-size:14px'>■</span> <b>IMPROCEDENTE</b><br>"
        f"<span style='color:{COR_IMP};font-size:18px'><b>{_fmt_int(improc)}</b></span><br><br>"
        f"<span style='color:{COR_OUT};font-size:14px'>■</span> <b>OUTROS</b><br>"
        f"<span style='color:{COR_OUT};font-size:18px'><b>{_fmt_int(outros)}</b></span><br><br>"
        f"<span style='color:#fcba03;font-size:12px'><b>TOTAL</b></span><br>"
        f"<span style='color:#fcba03;font-size:20px'><b>{_fmt_int(total)}</b></span>"
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=box_x, y=box_y,
        xanchor="right", yanchor="top",
        text=txt,
        showarrow=False,
        align="left",
        bgcolor="rgba(0,0,0,0.45)",
        bordercolor="rgba(255,255,255,0.18)",
        borderwidth=1,
        borderpad=10,
    )
    return fig


# ------------------------------------------------------
# UI do bloco
# ------------------------------------------------------
st.markdown('<div class="card"><div class="card-title">RELATÓRIOS GERENCIAIS</div>', unsafe_allow_html=True)

if "show_relatorios" not in st.session_state:
    st.session_state.show_relatorios = False

c1, c2 = st.columns([1.2, 4.8])
with c1:
    if st.button("📑 Abrir / Fechar Relatórios"):
        st.session_state.show_relatorios = not st.session_state.show_relatorios
with c2:
    st.caption("Relatórios respeitam período/UF. Comparativo Anual usa a base completa (df).")

if st.session_state.show_relatorios:
    tab_reg, tab_uf, tab_ano = st.tabs(["📍 Regional", "🗺️ Estado (UF)", "📅 Comparativo Anual"])

    # ==================================================
    # TAB 1 — REGIONAL
    # ==================================================
    with tab_reg:
        st.subheader("Relatório por Regional")

        if not _col_ok(COL_REGIONAL):
            st.warning("Coluna REGIONAL não encontrada.")
        else:
            base = df_periodo.dropna(subset=[COL_REGIONAL]).copy()
            if base.empty:
                st.info("Sem dados no período.")
            else:
                base[COL_REGIONAL] = _norm(base[COL_REGIONAL])
                base = _classificar(base)

                modo = st.selectbox(
                    "Modo",
                    ["Todas (por regional)", "Uma regional (detalhe por resultado)"],
                    index=0,
                    key="rg_modo_reg"
                )

                # posição do box (regional)
                BOX_X_REG = 1.0  # <-- mova p/ direita/esquerda
                BOX_Y_REG = 0.98  # <-- mova p/ cima/baixo

                if modo == "Uma regional (detalhe por resultado)":
                    regs = sorted(base[COL_REGIONAL].unique().tolist())
                    reg_sel = st.selectbox("Regional", regs, index=0, key="rg_reg_sel")
                    rec = base[base[COL_REGIONAL] == reg_sel]

                    tab = (
                        rec.groupby("_CLASSE_")
                        .size()
                        .reindex(["PROCEDENTE", "IMPROCEDENTE", "OUTROS"], fill_value=0)
                        .reset_index(name="QTD")
                    )
                    total = int(tab["QTD"].sum()) or 1
                    tab["PCT"] = (tab["QTD"] / total * 100).round(1)

                    fig = px.bar(
                        tab,
                        x="_CLASSE_",
                        y="QTD",
                        color="_CLASSE_",
                        template="plotly_dark",
                        color_discrete_map={
                            "PROCEDENTE": COR_PROC,
                            "IMPROCEDENTE": COR_IMP,
                            "OUTROS": COR_OUT,
                        },
                    )

                    # QTD dentro
                    tab["TXT_QTD"] = tab["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))
                    fig.update_traces(text=tab["TXT_QTD"], textposition="inside", insidetextanchor="middle", cliponaxis=False)

                    # % em cima (simples aqui)
                    y_max = int(tab["QTD"].max()) if int(tab["QTD"].max()) > 0 else 1
                    pad = y_max * 0.10
                    fig.add_scatter(
                        x=tab["_CLASSE_"],
                        y=tab["QTD"].astype(float) + pad,
                        mode="text",
                        text=[("" if q == 0 else f"{p:.1f}%") for q, p in zip(tab["QTD"], tab["PCT"])],
                        textposition="middle center",
                        showlegend=False,
                        textfont=dict(size=11, family="Arial Black", color="white"),
                        hoverinfo="skip",
                    )

                    fig = _style_clean(fig)
                    fig = _legend_bottom(fig, y=-0.22)
                    fig.update_layout(margin=dict(l=10, r=180, t=30, b=80))  # r=180 reserva espaço pro box

                    # ✅ quadro em TODOS os 3 relatórios
                    proc_total = int(tab.loc[tab["_CLASSE_"] == "PROCEDENTE", "QTD"].sum())
                    improc_total = int(tab.loc[tab["_CLASSE_"] == "IMPROCEDENTE", "QTD"].sum())
                    outros_total = int(tab.loc[tab["_CLASSE_"] == "OUTROS", "QTD"].sum())
                    total_geral = proc_total + improc_total + outros_total
                    fig = _add_summary_box(fig, proc_total, improc_total, outros_total, total_geral, box_x=BOX_X_REG, box_y=BOX_Y_REG)

                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        tab.rename(columns={"_CLASSE_": "RESULTADO", "PCT": "%"}),
                        hide_index=True,
                        use_container_width=True
                    )

                else:
                    tab = (
                        base.groupby([COL_REGIONAL, "_CLASSE_"])
                        .size()
                        .unstack(fill_value=0)
                        .reset_index()
                    )
                    for c in ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"]:
                        if c not in tab.columns:
                            tab[c] = 0
                    tab["TOTAL"] = tab["PROCEDENTE"] + tab["IMPROCEDENTE"] + tab["OUTROS"]
                    tab = tab.sort_values("TOTAL", ascending=False)

                    top_n = st.slider("Top N regionais", 5, 40, 15, key="rg_reg_topn")
                    tab_top = tab.head(top_n).copy()

                    total_geral = int(tab_top["TOTAL"].sum()) or 1
                    tab_top["PCT_TOTAL"] = (tab_top["TOTAL"] / total_geral * 100).round(1)

                    melt = tab_top.melt(
                        id_vars=[COL_REGIONAL, "TOTAL", "PCT_TOTAL"],
                        value_vars=["PROCEDENTE", "IMPROCEDENTE", "OUTROS"],
                        var_name="RESULTADO",
                        value_name="QTD"
                    )
                    melt["TXT_QTD"] = melt["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))

                    fig = px.bar(
                        melt,
                        x=COL_REGIONAL,
                        y="QTD",
                        color="RESULTADO",
                        barmode="stack",
                        template="plotly_dark",
                        color_discrete_map={
                            "PROCEDENTE": COR_PROC,
                            "IMPROCEDENTE": COR_IMP,
                            "OUTROS": COR_OUT,
                        },
                    )
                    fig.update_traces(text=melt["TXT_QTD"], textposition="inside", insidetextanchor="middle", cliponaxis=False)

                    # % em cima do total da regional (scatter alinhado porque x é único)
                    y_max = int(tab_top["TOTAL"].max()) if int(tab_top["TOTAL"].max()) > 0 else 1
                    pad = y_max * 0.04
                    fig.add_scatter(
                        x=tab_top[COL_REGIONAL],
                        y=tab_top["TOTAL"].astype(float) + pad,
                        mode="text",
                        text=[f"{p:.1f}%" for p in tab_top["PCT_TOTAL"]],
                        textposition="middle center",
                        showlegend=False,
                        textfont=dict(size=11, family="Arial Black", color="white"),
                        hoverinfo="skip",
                    )

                    fig = _style_clean(fig)
                    fig = _legend_bottom(fig, y=-0.22)
                    fig.update_layout(margin=dict(l=10, r=180, t=30, b=80))

                    # ✅ quadro (soma do recorte Top N)
                    proc_total = int(tab_top["PROCEDENTE"].sum())
                    improc_total = int(tab_top["IMPROCEDENTE"].sum())
                    outros_total = int(tab_top["OUTROS"].sum())
                    total_geral2 = proc_total + improc_total + outros_total
                    fig = _add_summary_box(fig, proc_total, improc_total, outros_total, total_geral2, box_x=BOX_X_REG, box_y=BOX_Y_REG)

                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(tab_top, hide_index=True, use_container_width=True)

    # ==================================================
    # TAB 2 — UF
    # ==================================================
    with tab_uf:
        st.subheader("Relatório por Estado (UF)")

        if not _col_ok(COL_ESTADO):
            st.warning("Coluna ESTADO/UF não encontrada.")
        else:
            base = df_periodo.dropna(subset=[COL_ESTADO]).copy()
            if base.empty:
                st.info("Sem dados no período.")
            else:
                base[COL_ESTADO] = _norm(base[COL_ESTADO])
                base = _classificar(base)

                tab = (
                    base.groupby([COL_ESTADO, "_CLASSE_"])
                    .size()
                    .unstack(fill_value=0)
                    .reset_index()
                )
                for c in ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"]:
                    if c not in tab.columns:
                        tab[c] = 0
                tab["TOTAL"] = tab["PROCEDENTE"] + tab["IMPROCEDENTE"] + tab["OUTROS"]
                tab = tab.sort_values("TOTAL", ascending=False)

                top_n = st.slider("Top N UFs", 5, 30, 15, key="rg_uf_topn")
                tab_top = tab.head(top_n).copy()

                total_geral = int(tab_top["TOTAL"].sum()) or 1
                tab_top["PCT_TOTAL"] = (tab_top["TOTAL"] / total_geral * 100).round(1)

                melt = tab_top.melt(
                    id_vars=[COL_ESTADO, "TOTAL", "PCT_TOTAL"],
                    value_vars=["PROCEDENTE", "IMPROCEDENTE", "OUTROS"],
                    var_name="RESULTADO",
                    value_name="QTD"
                )
                melt["TXT_QTD"] = melt["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))

                fig = px.bar(
                    melt,
                    x=COL_ESTADO,
                    y="QTD",
                    color="RESULTADO",
                    barmode="stack",
                    template="plotly_dark",
                    color_discrete_map={
                        "PROCEDENTE": COR_PROC,
                        "IMPROCEDENTE": COR_IMP,
                        "OUTROS": COR_OUT,
                    }
                )
                fig.update_traces(text=melt["TXT_QTD"], textposition="inside", insidetextanchor="middle", cliponaxis=False)

                # % em cima do total da UF
                y_max = int(tab_top["TOTAL"].max()) if int(tab_top["TOTAL"].max()) > 0 else 1
                pad = y_max * 0.03
                fig.add_scatter(
                    x=tab_top[COL_ESTADO],
                    y=tab_top["TOTAL"].astype(float) + pad,
                    mode="text",
                    text=[f"{p:.1f}%" for p in tab_top["PCT_TOTAL"]],
                    textposition="middle center",
                    showlegend=False,
                    textfont=dict(size=11, family="Arial Black", color="white"),
                    hoverinfo="skip",
                )

                fig = _style_clean(fig)
                fig = _legend_bottom(fig, y=-0.22)
                fig.update_layout(margin=dict(l=10, r=180, t=30, b=80))

                # posição do box (UF)
                BOX_X_UF = 1.05  # <-- mova p/ direita/esquerda
                BOX_Y_UF = 0.98  # <-- mova p/ cima/baixo

                # ✅ quadro (soma do recorte Top N)
                proc_total = int(tab_top["PROCEDENTE"].sum())
                improc_total = int(tab_top["IMPROCEDENTE"].sum())
                outros_total = int(tab_top["OUTROS"].sum())
                total_geral2 = proc_total + improc_total + outros_total
                fig = _add_summary_box(fig, proc_total, improc_total, outros_total, total_geral2, box_x=BOX_X_UF, box_y=BOX_Y_UF)

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(tab, hide_index=True, use_container_width=True)

    # ==================================================
    # TAB 3 — COMPARATIVO ANUAL
    # ==================================================
    with tab_ano:
        st.subheader("Comparativo Anual — Procedente x Improcedente x Outros")

        if not _col_ok(COL_DATA):
            st.warning("Coluna DATA não encontrada.")
        else:
            base = df.copy()
            base[COL_DATA] = pd.to_datetime(base[COL_DATA], errors="coerce", dayfirst=True)
            base = base.dropna(subset=[COL_DATA]).copy()

            if base.empty:
                st.info("Sem datas válidas.")
            else:
                base = _classificar(base)
                base["ANO"] = base[COL_DATA].dt.year.astype(int)

                if _col_ok(COL_ESTADO):
                    base[COL_ESTADO] = _norm(base[COL_ESTADO])
                    ufs_disp = ["TOTAL"] + sorted(base[COL_ESTADO].dropna().unique().tolist())
                    idx = ufs_disp.index(uf_sel) if isinstance(uf_sel, str) and uf_sel in ufs_disp else 0
                    uf_comp = st.selectbox("Filtrar UF (opcional)", options=ufs_disp, index=idx, key="cmp_ano_uf")
                    if uf_comp != "TOTAL":
                        base = base[base[COL_ESTADO] == uf_comp].copy()

                tab = (
                    base.groupby(["ANO", "_CLASSE_"])
                    .size()
                    .reset_index(name="QTD")
                )

                if tab.empty:
                    st.info("Sem dados para o comparativo anual.")
                else:
                    classes = ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"]
                    anos = sorted(tab["ANO"].unique().tolist())

                    grid = (
                        pd.DataFrame({"ANO": anos}).assign(_k=1)
                        .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
                        .drop(columns="_k")
                    )
                    tab = grid.merge(tab, on=["ANO", "_CLASSE_"], how="left").fillna({"QTD": 0})
                    tab["QTD"] = tab["QTD"].astype(int)

                    total_ano = tab.groupby("ANO")["QTD"].transform("sum").replace(0, 1)
                    tab["PCT"] = (tab["QTD"] / total_ano * 100).round(1)

                    tab["TXT_QTD"] = tab["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))
                    tab["TXT_PCT"] = tab.apply(lambda r: "" if int(r["QTD"]) == 0 else f'{r["PCT"]:.1f}%', axis=1)

                    # gráfico base: QTD dentro
                    fig = px.bar(
                        tab,
                        x="ANO",
                        y="QTD",
                        color="_CLASSE_",
                        barmode="group",
                        template="plotly_dark",
                        category_orders={"_CLASSE_": classes},
                        color_discrete_map={
                            "PROCEDENTE": COR_PROC,
                            "IMPROCEDENTE": COR_IMP,
                            "OUTROS": COR_OUT,
                        },
                    )
                    fig.update_traces(
                        text=tab["TXT_QTD"],
                        textposition="inside",
                        insidetextanchor="middle",
                        cliponaxis=False
                    )

                    # ✅ % ALINHADA: trace invisível só para % (usa o mesmo offset do group)
                    fig_pct = px.bar(
                        tab,
                        x="ANO",
                        y="QTD",
                        color="_CLASSE_",
                        barmode="group",
                        template="plotly_dark",
                        category_orders={"_CLASSE_": classes},
                        color_discrete_map={
                            "PROCEDENTE": "rgba(0,0,0,0)",
                            "IMPROCEDENTE": "rgba(0,0,0,0)",
                            "OUTROS": "rgba(0,0,0,0)",
                        },
                    )
                    fig_pct.update_traces(
                        marker_line_width=0,
                        marker_opacity=0,
                        text=tab["TXT_PCT"],
                        textposition="outside",
                        cliponaxis=False,
                        showlegend=False,
                        hoverinfo="skip",
                        textfont=dict(size=11, family="Arial Black", color="white"),
                    )
                    for tr in fig_pct.data:
                        fig.add_trace(tr)

                    fig = _style_clean(fig)

                    # legenda embaixo + margem direita pro box + margem inferior da legenda
                    fig = _legend_bottom(fig, y=-0.22)
                    fig.update_layout(margin=dict(l=10, r=220, t=30, b=80))

                    # posição do box (ANUAL)
                    BOX_X_ANO = 1.05  # <-- aumente (1.30) para ir mais à direita; diminua (1.05) para esquerda
                    BOX_Y_ANO = 0.98  # <-- aumente para subir; diminua para descer

                    proc_total = int(tab.loc[tab["_CLASSE_"] == "PROCEDENTE", "QTD"].sum())
                    improc_total = int(tab.loc[tab["_CLASSE_"] == "IMPROCEDENTE", "QTD"].sum())
                    outros_total = int(tab.loc[tab["_CLASSE_"] == "OUTROS", "QTD"].sum())
                    total_geral2 = proc_total + improc_total + outros_total

                    # ✅ quadro em TODOS os 3 relatórios
                    fig = _add_summary_box(fig, proc_total, improc_total, outros_total, total_geral2, box_x=BOX_X_ANO, box_y=BOX_Y_ANO)

                    st.plotly_chart(fig, use_container_width=True)

                    # tabela
                    piv = (
                        tab.pivot_table(index="ANO", columns="_CLASSE_", values="QTD", aggfunc="sum", fill_value=0)
                        .reset_index()
                    )
                    for c in classes:
                        if c not in piv.columns:
                            piv[c] = 0
                    piv["TOTAL"] = piv["PROCEDENTE"] + piv["IMPROCEDENTE"] + piv["OUTROS"]

                    den = piv["TOTAL"].replace(0, 1)
                    piv["%PROCEDENTE"] = (piv["PROCEDENTE"] / den * 100).round(1)
                    piv["%IMPROCEDENTE"] = (piv["IMPROCEDENTE"] / den * 100).round(1)
                    piv["%OUTROS"] = (piv["OUTROS"] / den * 100).round(1)

                    st.dataframe(piv, hide_index=True, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# TAB 4 — DISTRIBUIDORA POR MÊS
# (usa COL_ESTADO como "Distribuidora")
# ==================================================
with tab_dist_mes:
    st.subheader("Distribuidora por Mês (AM/AS) — Procedente/Improcedente/Outros + Totais")

    if not _col_ok(COL_DATA) or not _col_ok(COL_ESTADO):
        st.warning("Preciso das colunas DATA e ESTADO/UF (usada aqui como 'Distribuidora').")
    else:
        base = df_periodo.copy()
        base[COL_DATA] = pd.to_datetime(base[COL_DATA], errors="coerce", dayfirst=True)
        base = base.dropna(subset=[COL_DATA]).copy()

        if base.empty:
            st.info("Sem dados com DATA válida no período.")
        else:
            base = _classificar(base)
            base[COL_ESTADO] = _norm(base[COL_ESTADO])

            # filtros
            anos = sorted(base[COL_DATA].dt.year.dropna().unique().astype(int).tolist())
            ano_sel2 = st.selectbox("Ano", anos, index=len(anos)-1 if anos else 0, key="dist_mes_ano")

            base = base[base[COL_DATA].dt.year == int(ano_sel2)].copy()

            # top N distribuidoras (para não ficar poluído)
            top_n = st.slider("Top N distribuidoras", 3, 30, 10, key="dist_mes_topn")

            # pega TOP N por volume anual
            top = (
                base.groupby(COL_ESTADO)
                .size()
                .sort_values(ascending=False)
                .head(top_n)
                .index
                .tolist()
            )
            base = base[base[COL_ESTADO].isin(top)].copy()

            # mês
            base["MES_NUM"] = base[COL_DATA].dt.month
            base["MÊS"] = base["MES_NUM"].map(MESES_PT)

            # agregado: mês x distribuidora x classe
            tab = (
                base.groupby(["MES_NUM", "MÊS", COL_ESTADO, "_CLASSE_"])
                .size()
                .reset_index(name="QTD")
            )

            if tab.empty:
                st.info("Sem dados para este ano/top N.")
            else:
                # garante meses 1..12 e classes
                classes = ["PROCEDENTE", "IMPROCEDENTE", "OUTROS"]
                meses_df = pd.DataFrame({"MES_NUM": list(range(1, 13))})
                meses_df["MÊS"] = meses_df["MES_NUM"].map(MESES_PT)

                grid = (
                    meses_df.assign(_k=1)
                    .merge(pd.DataFrame({COL_ESTADO: top}).assign(_k=1), on="_k")
                    .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
                    .drop(columns="_k")
                )

                tab = (
                    grid.merge(tab, on=["MES_NUM", "MÊS", COL_ESTADO, "_CLASSE_"], how="left")
                    .fillna({"QTD": 0})
                )
                tab["QTD"] = tab["QTD"].astype(int)

                # total do mês (para % em cima)
                total_mes = tab.groupby(["MES_NUM", "MÊS"])["QTD"].transform("sum").replace(0, 1)
                tab["PCT_MES"] = (tab["QTD"] / total_mes * 100).round(1)

                # QTD dentro
                tab["TXT_QTD"] = tab["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))

                # gráfico: empilhado por CLASSE, facet por DISTRIBUIDORA (1 gráfico por distribuidora)
                fig = px.bar(
                    tab.sort_values("MES_NUM"),
                    x="MÊS",
                    y="QTD",
                    color="_CLASSE_",
                    barmode="stack",
                    facet_col=COL_ESTADO,
                    facet_col_wrap=2,
                    template="plotly_dark",
                    category_orders={"MÊS": MESES_ORDEM, "_CLASSE_": classes},
                    color_discrete_map={
                        "PROCEDENTE": COR_PROC,
                        "IMPROCEDENTE": COR_IMP,
                        "OUTROS": COR_OUT,
                    }
                )

                fig.update_traces(
                    text=tab["TXT_QTD"],
                    textposition="inside",
                    insidetextanchor="middle",
                    cliponaxis=False
                )

                # limpa grid/eixo esquerdo e títulos repetidos
                fig.for_each_yaxis(lambda a: a.update(visible=False, showticklabels=False, showgrid=False, zeroline=False))
                fig.for_each_xaxis(lambda a: a.update(showgrid=False, ticks=""))
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")

                # legenda embaixo (padronizada)
                fig = _legend_bottom(fig, y=-0.18)
                fig.update_layout(margin=dict(l=10, r=220, t=40, b=90))

                # quadro total (recorte atual)
                proc_total = int(tab.loc[tab["_CLASSE_"] == "PROCEDENTE", "QTD"].sum())
                improc_total = int(tab.loc[tab["_CLASSE_"] == "IMPROCEDENTE", "QTD"].sum())
                outros_total = int(tab.loc[tab["_CLASSE_"] == "OUTROS", "QTD"].sum())
                total_geral = proc_total + improc_total + outros_total

                # ajuste posição se quiser
                BOX_X_MES = 1.22  # maior = mais direita / menor = mais esquerda
                BOX_Y_MES = 0.98  # maior = sobe / menor = desce
                fig = _add_summary_box(fig, proc_total, improc_total, outros_total, total_geral, box_x=BOX_X_MES, box_y=BOX_Y_MES)

                st.plotly_chart(fig, use_container_width=True)

                # tabela resumo (mês total por distribuidora)
                resumo = (
                    tab.groupby(["MÊS", COL_ESTADO])["QTD"]
                    .sum()
                    .reset_index()
                )
                st.dataframe(resumo, hide_index=True, use_container_width=True)



# ======================================================
# EXPORTAR DASHBOARD (PRINT PARA PDF) - OPÇÃO A
# ======================================================
st.markdown("""
<style>
@media print {
  header, footer, [data-testid="stSidebar"], [data-testid="stToolbar"] { display: none !important; }
  .no-print { display: none !important; }
  .block-container { max-width: 100% !important; padding: 0 !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.button("🖨️ Exportar dashboard (print em PDF)")
st.markdown('</div>', unsafe_allow_html=True)

components.html(
    """
    <script>
      const btns = window.parent.document.querySelectorAll('button');
      const target = Array.from(btns).find(b => b.innerText.trim() === '🖨️ Exportar dashboard (print em PDF)');
      if (target && !target.dataset.printBound) {
        target.dataset.printBound = "1";
        target.addEventListener('click', () => {
          window.parent.focus();
          window.parent.print();
        });
      }
    </script>
    """,
    height=0
)
