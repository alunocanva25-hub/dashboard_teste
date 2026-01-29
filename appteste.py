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

# ==================================================
# RELATÓRIOS GERENCIAIS (CORRIGIDO)
# ✅ Corrige bug: "IMPROCEDENTE" contém "PROCEDENTE"
# ✅ Remove OUTROS definitivamente (não existe na sua base)
# ✅ QTD dentro das barras (por segmento correto)
# ✅ % no topo (participação do TOTAL da coluna no total do relatório)
# ✅ Legenda embaixo (padrão)
# ✅ Sem grade e sem eixo Y (esquerdo)
# ✅ Quadro de totais à direita (comentado p/ mover)
# ✅ Demanda x Demandas (Geral): X vs RESTANTE + filtro AM/AS/AMBOS só nele
# ✅ Distribuidora por Mês: títulos só UF/Estado + meses em todos os facets
# ==================================================

import numpy as np

# ==================================================
# HELPERS
# ==================================================
def _fmt_int(v: int) -> str:
    return f"{int(v):,}".replace(",", ".")

def classificar_resultado(df: pd.DataFrame, col_res: str = "_RES_") -> pd.DataFrame:
    """
    ✅ CORREÇÃO DEFINITIVA:
    'IMPROCEDENTE' contém 'PROCEDENTE' -> precisa classificar na ordem correta.
    OUTROS não é usado (mas mantemos o default para segurança).
    """
    d = df.copy()
    res = d[col_res].astype(str).str.upper().str.strip()

    mask_improc = res.str.contains("IMPROCED", na=False)
    mask_proc = res.str.contains("PROCED", na=False) & (~mask_improc)

    d["_CLASSE_"] = np.where(mask_improc, "IMPROCEDENTE",
                     np.where(mask_proc, "PROCEDENTE", "OUTROS"))
    return d

def _make_tab_counts_sem_outros(base_df: pd.DataFrame, dim_col: str) -> pd.DataFrame:
    """
    Retorna tab com colunas: DIM, _CLASSE_, QTD
    Mantém só PROCEDENTE e IMPROCEDENTE (OUTROS removido definitivamente).
    """
    if base_df is None or base_df.empty:
        return pd.DataFrame(columns=["DIM", "_CLASSE_", "QTD"])

    df0 = base_df.copy()

    if "_RES_" not in df0.columns:
        return pd.DataFrame(columns=["DIM", "_CLASSE_", "QTD"])

    df0 = classificar_resultado(df0, "_RES_")
    df0 = df0[df0["_CLASSE_"].isin(["PROCEDENTE", "IMPROCEDENTE"])].copy()
    if df0.empty:
        return pd.DataFrame(columns=["DIM", "_CLASSE_", "QTD"])

    df0["DIM"] = df0[dim_col].astype(str).str.upper().str.strip()

    tab = (
        df0.groupby(["DIM", "_CLASSE_"])
        .size()
        .reset_index(name="QTD")
    )
    return tab

def _plot_stack_with_pct_and_box_sem_outros(
    tab: pd.DataFrame,
    x_title: str,
    chart_title: str,
    category_order: list | None = None,
    box_x: float = 1.18,  # 👉 maior -> mais p/ DIREITA | menor -> mais p/ ESQUERDA
    box_y: float = 0.98,  # 👉 maior -> mais p/ CIMA    | menor -> mais p/ BAIXO
):
    """
    tab: colunas [DIM, _CLASSE_, QTD] com PROCEDENTE/IMPROCEDENTE
    - QTD dentro (por segmento correto)
    - % no topo = participação do TOTAL da coluna no total geral do relatório
    - legenda embaixo
    - sem grid e sem eixo Y
    - quadro totais à direita (procedente/improcedente/total)
    """
    if tab is None or tab.empty:
        return None

    classes = ["PROCEDENTE", "IMPROCEDENTE"]

    dims = tab["DIM"].unique().tolist()
    if category_order:
        dims = [d for d in category_order if d in dims] + [d for d in dims if d not in category_order]

    # grid completo para não “sumir” classe
    grid = (
        pd.DataFrame({"DIM": dims}).assign(_k=1)
        .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
        .drop(columns="_k")
    )
    tab2 = grid.merge(tab, on=["DIM", "_CLASSE_"], how="left").fillna({"QTD": 0})
    tab2["QTD"] = tab2["QTD"].astype(int)
    tab2["TXT_QTD"] = tab2["QTD"].apply(lambda v: "" if int(v) == 0 else str(int(v)))

    fig = px.bar(
        tab2,
        x="DIM",
        y="QTD",
        color="_CLASSE_",
        barmode="stack",
        template="plotly_dark",
        category_orders={"DIM": dims, "_CLASSE_": classes},
        color_discrete_map={"PROCEDENTE": COR_PROC, "IMPROCEDENTE": COR_IMP},
        title=chart_title,
    )

    # ✅ aplica texto POR TRACE (evita “vazar” o mesmo número no verde/vermelho)
    for tr in fig.data:
        classe = tr.name
        txt = []
        for dim in tr.x:
            v = tab2.loc[(tab2["DIM"] == dim) & (tab2["_CLASSE_"] == classe), "TXT_QTD"]
            txt.append(v.iloc[0] if len(v) else "")
        tr.text = txt
        tr.textposition = "inside"
        tr.insidetextanchor = "middle"
        tr.cliponaxis = False

    # remove eixo Y e grades
    fig.update_yaxes(visible=False, showticklabels=False, showgrid=False, zeroline=False)
    fig.update_xaxes(showgrid=False, ticks="")

    # legenda embaixo (padrão)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="left",
            x=0.0
        ),
        margin=dict(l=10, r=230, t=50, b=85),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(xaxis_title=x_title, yaxis_title="")

    # % no topo: participação do TOTAL daquela coluna no total geral
    tot_por_dim = tab2.groupby("DIM")["QTD"].sum().reindex(dims).fillna(0).astype(int)
    grand_total = int(tot_por_dim.sum()) if int(tot_por_dim.sum()) > 0 else 1
    pct_por_dim = (tot_por_dim / grand_total * 100).round(1)

    y_max = int(tot_por_dim.max()) if int(tot_por_dim.max()) > 0 else 1
    pad = max(5, int(y_max * 0.06))

    for dim in dims:
        tot = int(tot_por_dim.loc[dim])
        if tot <= 0:
            continue
        fig.add_annotation(
            x=dim, xref="x",
            y=tot + pad, yref="y",
            text=f"<b>{pct_por_dim.loc[dim]:.1f}%</b>",
            showarrow=False,
            font=dict(size=12, color="white", family="Arial Black"),
            align="center"
        )

    # quadro totais (direita)
    proc_total = int(tab2.loc[tab2["_CLASSE_"] == "PROCEDENTE", "QTD"].sum())
    imp_total  = int(tab2.loc[tab2["_CLASSE_"] == "IMPROCEDENTE", "QTD"].sum())
    total_all  = proc_total + imp_total

    fig.add_annotation(
        xref="paper", yref="paper",
        x=box_x, y=box_y,
        showarrow=False, align="left",
        bgcolor="rgba(0,0,0,0.45)",
        bordercolor="rgba(255,255,255,0.25)",
        borderwidth=1,
        borderpad=10,
        text=(
            f"<span style='color:{COR_PROC};font-size:13px'><b>■ PROCEDENTE</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(proc_total)}</b></span><br><br>"
            f"<span style='color:{COR_IMP};font-size:13px'><b>■ IMPROCEDENTE</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(imp_total)}</b></span><br><br>"
            f"<span style='color:#fcba03;font-size:13px'><b>TOTAL</b></span><br>"
            f"<span style='color:#fcba03;font-size:20px'><b>{_fmt_int(total_all)}</b></span>"
        )
    )

    return fig

# ==================================================
# ABAS (RELATÓRIOS GERENCIAIS)
# ==================================================
st.markdown('<div class="card"><div class="card-title">RELATÓRIOS GERENCIAIS</div>', unsafe_allow_html=True)

tab_regional, tab_uf, tab_anual, tab_dist_mes, tab_demanda = st.tabs(
    ["📍 Regional", "🗺️ Estado (UF)", "📅 Comparativo Anual", "📆 Distribuidora por Mês", "📌 Demanda x Demandas (Geral)"]
)

# ==================================================
# 📍 REGIONAL
# ==================================================
with tab_regional:
    st.subheader("📍 Regional — Procedente x Improcedente")

    if COL_REGIONAL is None:
        st.warning("Coluna REGIONAL não encontrada.")
    else:
        tab = _make_tab_counts_sem_outros(df_filtro, COL_REGIONAL)

        if tab.empty:
            st.info("Sem dados para Regional.")
        else:
            # ordena por total desc (opcional)
            ordem = (
                tab.groupby("DIM")["QTD"].sum()
                .sort_values(ascending=False)
                .index.tolist()
            )
            fig = _plot_stack_with_pct_and_box_sem_outros(
                tab,
                x_title="REGIONAL",
                chart_title="📍 Regional — Procedente x Improcedente",
                category_order=ordem,
                box_x=1.18,  # ajuste direita/esquerda
                box_y=0.98,  # ajuste cima/baixo
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================================================
# 🗺️ ESTADO (UF)
# ==================================================
with tab_uf:
    st.subheader("🗺️ Estado (UF) — Procedente x Improcedente")

    if COL_ESTADO is None:
        st.warning("Coluna ESTADO/UF não encontrada.")
    else:
        tab = _make_tab_counts_sem_outros(df_filtro, COL_ESTADO)

        if tab.empty:
            st.info("Sem dados para UF.")
        else:
            ordem = (
                tab.groupby("DIM")["QTD"].sum()
                .sort_values(ascending=False)
                .index.tolist()
            )
            fig = _plot_stack_with_pct_and_box_sem_outros(
                tab,
                x_title="LOCALIDADE",
                chart_title="🗺️ Estado (UF) — Procedente x Improcedente",
                category_order=ordem,
                box_x=1.18,
                box_y=0.98,
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================================================
# 📅 COMPARATIVO ANUAL — Procedente x Improcedente
# - QTD dentro
# - % alinhada acima (cada barra no seu lugar)
# - legenda embaixo
# - quadro totais à direita (X/Y ajustáveis)
# - SEM OUTROS
# - fig_ano isolado (não interfere nos outros relatórios)
# ==================================================

try:
    _ano_container = tab_ano
except Exception:
    _ano_container = st.container()

with _ano_container:
    st.subheader("📅 Comparativo Anual — Procedente x Improcedente")

    # ---------- helpers locais ----------
    def _col_ok_local(c):
        try:
            return c is not None and str(c).strip() != "" and c in df.columns
        except Exception:
            return False

    def _norm_txt(s):
        return s.astype(str).str.upper().str.strip()

    def _fmt_int(n: int) -> str:
        return f"{int(n):,}".replace(",", ".")

    # ---------- validações ----------
    if not _col_ok_local(COL_DATA):
        st.warning("Coluna DATA não encontrada.")
        st.stop()

    base = df.copy()
    base[COL_DATA] = pd.to_datetime(base[COL_DATA], errors="coerce", dayfirst=True)
    base = base.dropna(subset=[COL_DATA]).copy()

    if base.empty:
        st.info("Sem datas válidas.")
        st.stop()

    # ---------- coluna de RESULTADO ----------
    if "_RES_" in base.columns:
        res = _norm_txt(base["_RES_"].fillna(""))
    elif _col_ok_local(COL_RESULTADO):
        res = _norm_txt(base[COL_RESULTADO].fillna(""))
    else:
        st.warning("Não encontrei a coluna de RESULTADO (nem _RES_ nem COL_RESULTADO).")
        st.stop()

    # ==================================================
    # ✅ CLASSIFICAÇÃO CORRETA:
    # IMPROCEDENTE contém "PROCEDENTE", então:
    # 1) marca IMPROCEDENTE primeiro
    # 2) marca PROCEDENTE somente se NÃO for improcedente
    # ==================================================
    mask_improc = res.str.contains("IMPROCED", na=False)
    mask_proc = res.str.contains("PROCED", na=False) & (~mask_improc)

    base["_CLASSE_"] = None
    base.loc[mask_proc, "_CLASSE_"] = "PROCEDENTE"
    base.loc[mask_improc, "_CLASSE_"] = "IMPROCEDENTE"

    base = base[base["_CLASSE_"].isin(["PROCEDENTE", "IMPROCEDENTE"])].copy()
    if base.empty:
        st.warning("Não sobraram registros classificados como PROCEDENTE/IMPROCEDENTE.")
        st.stop()

    base["ANO"] = base[COL_DATA].dt.year.astype(int)

    # ---------- filtro UF opcional ----------
    if _col_ok_local(COL_ESTADO):
        base[COL_ESTADO] = _norm_txt(base[COL_ESTADO])
        ufs_disp = ["TOTAL"] + sorted(base[COL_ESTADO].dropna().unique().tolist())

        try:
            idx = ufs_disp.index(uf_sel) if isinstance(uf_sel, str) and uf_sel in ufs_disp else 0
        except Exception:
            idx = 0

        uf_comp = st.selectbox("Filtrar UF (opcional)", options=ufs_disp, index=idx, key="cmp_ano_uf")
        if uf_comp != "TOTAL":
            base = base[base[COL_ESTADO] == uf_comp].copy()

    # ---------- agrega ----------
    tab = (
        base.groupby(["ANO", "_CLASSE_"])
        .size()
        .reset_index(name="QTD")
    )

    if tab.empty:
        st.info("Sem dados para o comparativo anual.")
        st.stop()

    classes = ["PROCEDENTE", "IMPROCEDENTE"]
    anos = sorted(tab["ANO"].unique().tolist())

    grid = (
        pd.DataFrame({"ANO": anos}).assign(_k=1)
        .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
        .drop(columns="_k")
    )
    tab = grid.merge(tab, on=["ANO", "_CLASSE_"], how="left").fillna({"QTD": 0})
    tab["QTD"] = tab["QTD"].astype(int)

    # % por ANO (denominador = total do ano)
    total_ano = tab.groupby("ANO")["QTD"].transform("sum").replace(0, 1)
    tab["PCT"] = (tab["QTD"] / total_ano * 100).round(1)

    # ==================================================
    # GRÁFICO (fig_ano isolado)
    # ==================================================
    fig_ano = px.bar(
        tab,
        x="ANO",
        y="QTD",
        color="_CLASSE_",
        barmode="group",
        template="plotly_dark",
        category_orders={"_CLASSE_": classes},
        color_discrete_map={"PROCEDENTE": COR_PROC, "IMPROCEDENTE": COR_IMP},
    )

    # QTD dentro das barras
    fig_ano.update_traces(
        texttemplate="%{y}",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
    )

    # ---------- % acima (ALINHADA POR BARRA) ----------
    # Ajustes:
    # - OFFSET_Y: sobe/abaixa a % em relação à barra
    # - SHIFT_PROC / SHIFT_IMP: move a % para esquerda/direita da barra do ano (porque é group)
    max_y = int(tab["QTD"].max()) if not tab.empty else 0
    OFFSET_Y = max(1, int(max_y * 0.05))  # ↑ maior = mais acima | menor = mais perto

    SHIFT_PROC = -18  # (←) mais negativo = mais para ESQUERDA
    SHIFT_IMP  = +18  # (→) mais positivo = mais para DIREITA

    for _, r in tab.iterrows():
        if int(r["QTD"]) == 0:
            continue

        xshift = SHIFT_PROC if r["_CLASSE_"] == "PROCEDENTE" else SHIFT_IMP

        fig_ano.add_annotation(
            x=r["ANO"],
            y=int(r["QTD"]) + OFFSET_Y,
            text=f'{float(r["PCT"]):.1f}%',
            showarrow=False,
            font=dict(size=12, color="white", family="Arial Black"),
            xanchor="center",
            yanchor="bottom",
            xshift=xshift,  # ✅ garante que cada % fique em cima da sua barra
        )

    # sem grid e sem eixo esquerdo
    fig_ano.update_xaxes(showgrid=False, ticks="")
    fig_ano.update_yaxes(showgrid=False, visible=False, ticks="", zeroline=False)

    # legenda embaixo
    LEGEND_Y = -0.22  # (↓) menor = mais pra baixo | maior = mais pra cima
    fig_ano.update_layout(
        legend=dict(orientation="h", y=LEGEND_Y, x=0, title_text=""),
        margin=dict(l=10, r=220, t=30, b=80),
    )

    # ---------- quadro totais à direita ----------
    proc_total = int(tab.loc[tab["_CLASSE_"] == "PROCEDENTE", "QTD"].sum())
    improc_total = int(tab.loc[tab["_CLASSE_"] == "IMPROCEDENTE", "QTD"].sum())
    total_geral = proc_total + improc_total

    # >>> AJUSTE POSIÇÃO DO QUADRO <<<
    BOX_X_ANO = 1.12  # (->) maior = mais DIREITA | menor = mais ESQUERDA
    BOX_Y_ANO = 0.98  # (^) maior = mais CIMA    | menor = mais BAIXO

    fig_ano.add_annotation(
        xref="paper", yref="paper",
        x=BOX_X_ANO, y=BOX_Y_ANO,
        showarrow=False, align="left",
        bgcolor="rgba(0,0,0,0.45)",
        bordercolor="rgba(255,255,255,0.25)",
        borderwidth=1,
        borderpad=10,
        text=(
            f"<span style='color:{COR_PROC};font-size:13px'><b>■ PROCEDENTE</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(proc_total)}</b></span><br><br>"
            f"<span style='color:{COR_IMP};font-size:13px'><b>■ IMPROCEDENTE</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(improc_total)}</b></span><br><br>"
            f"<span style='color:#fcba03;font-size:13px'><b>TOTAL</b></span><br>"
            f"<span style='color:#fcba03;font-size:20px'><b>{_fmt_int(total_geral)}</b></span>"
        )
    )

    st.plotly_chart(fig_ano, use_container_width=True)

    # ---------- tabela ----------
    piv = (
        tab.pivot_table(index="ANO", columns="_CLASSE_", values="QTD", aggfunc="sum", fill_value=0)
        .reset_index()
    )
    if "PROCEDENTE" not in piv.columns:
        piv["PROCEDENTE"] = 0
    if "IMPROCEDENTE" not in piv.columns:
        piv["IMPROCEDENTE"] = 0

    piv["TOTAL"] = piv["PROCEDENTE"] + piv["IMPROCEDENTE"]
    den = piv["TOTAL"].replace(0, 1)
    piv["%PROCEDENTE"] = (piv["PROCEDENTE"] / den * 100).round(1)
    piv["%IMPROCEDENTE"] = (piv["IMPROCEDENTE"] / den * 100).round(1)

    st.dataframe(piv, hide_index=True, use_container_width=True)



# ==================================================
# 📆 DISTRIBUIDORA POR MÊS (MELHORADO)
# - Remove OUTROS
# - Meses abreviados em TODOS os facets
# - QTD dentro (com corte mínimo p/ não poluir)
# - Títulos (UF) limpos e com SHIFT ajustável (sem sobrepor meses/barras)
# ==================================================
with tab_dist_mes:
    st.subheader("📆 Distribuidora por Mês")

    if COL_DATA is None or COL_ESTADO is None:
        st.warning("Preciso das colunas DATA e ESTADO/UF.")
    else:
        base = df_periodo.copy()  # aqui faz sentido usar o período selecionado
        base[COL_DATA] = pd.to_datetime(base[COL_DATA], errors="coerce", dayfirst=True)
        base = base.dropna(subset=[COL_DATA]).copy()

        if base.empty:
            st.info("Sem dados com DATA válida no período.")
        else:
            if "_RES_" not in base.columns:
                st.warning("Coluna interna '_RES_' não encontrada.")
            else:
                # classifica e remove OUTROS
                base = classificar_resultado(base, "_RES_")
                base = base[base["_CLASSE_"].isin(["PROCEDENTE", "IMPROCEDENTE"])].copy()

                if base.empty:
                    st.info("Sem dados (após remover OUTROS).")
                else:
                    base[COL_ESTADO] = base[COL_ESTADO].astype(str).str.upper().str.strip()

                    # meses abreviados
                    MESES_ABREV = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
                    MESES_ORDEM = [MESES_ABREV[i] for i in range(1, 13)]

                    anos = sorted(base[COL_DATA].dt.year.dropna().unique().astype(int).tolist())
                    ano_sel2 = st.selectbox("Ano", anos, index=len(anos)-1 if anos else 0, key="dist_mes_ano")

                    base = base[base[COL_DATA].dt.year == int(ano_sel2)].copy()

                    top_n = st.slider("Top N estados", 3, 30, 10, key="dist_mes_topn")

                    # Top por volume total no ano
                    top = (
                        base.groupby(COL_ESTADO)
                        .size()
                        .sort_values(ascending=False)
                        .head(top_n)
                        .index
                        .tolist()
                    )
                    base = base[base[COL_ESTADO].isin(top)].copy()

                    base["MES_NUM"] = base[COL_DATA].dt.month
                    base["MÊS"] = base["MES_NUM"].map(MESES_ABREV)

                    tab = (
                        base.groupby(["MES_NUM", "MÊS", COL_ESTADO, "_CLASSE_"])
                        .size()
                        .reset_index(name="QTD")
                    )

                    if tab.empty:
                        st.info("Sem dados para este ano/top N.")
                    else:
                        classes = ["PROCEDENTE", "IMPROCEDENTE"]

                        # garante 12 meses + classes por estado
                        meses_df = pd.DataFrame({"MES_NUM": list(range(1, 13))})
                        meses_df["MÊS"] = meses_df["MES_NUM"].map(MESES_ABREV)

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

                        # ✅ corte p/ texto dentro não poluir
                        MIN_LABEL = st.slider("Mostrar QTD dentro a partir de", 0, 300, 50, key="dist_mes_minlabel")
                        tab["TXT_QTD"] = tab["QTD"].apply(lambda v: "" if int(v) < int(MIN_LABEL) else str(int(v)))

                        fig = px.bar(
                            tab.sort_values("MES_NUM"),
                            x="MÊS",
                            y="QTD",
                            color="_CLASSE_",
                            barmode="stack",
                            facet_col=COL_ESTADO,
                            facet_col_wrap=2,
                            facet_col_spacing=0.06,   # ✅ espaçamento horizontal
                            facet_row_spacing=0.14,   # ✅ espaçamento vertical (deixa mais “respirado”)
                            template="plotly_dark",
                            category_orders={"MÊS": MESES_ORDEM, "_CLASSE_": classes},
                            color_discrete_map={"PROCEDENTE": COR_PROC, "IMPROCEDENTE": COR_IMP},
                        )

                        # texto por trace (sem “vazar”)
                        for tr in fig.data:
                            classe = tr.name
                            txt = []
                            for mes in tr.x:
                                # pega valor desse mês + classe (primeiro match)
                                v = tab.loc[(tab["MÊS"] == mes) & (tab["_CLASSE_"] == classe), "TXT_QTD"]
                                txt.append(v.iloc[0] if len(v) else "")
                            tr.text = txt
                            tr.textposition = "inside"
                            tr.insidetextanchor = "middle"
                            tr.cliponaxis = False

                        # sem grid e sem eixo Y
                        fig.for_each_yaxis(lambda a: a.update(visible=False, showticklabels=False, showgrid=False, zeroline=False))
                        fig.for_each_xaxis(lambda a: a.update(showgrid=False, ticks="", showticklabels=True, tickangle=0))

                        # legenda embaixo + layout mais claro
                        fig.update_layout(
                            bargap=0.25,
                            legend=dict(
                                orientation="h",
                                yanchor="top",
                                y=-0.18,
                                xanchor="left",
                                x=0.0
                            ),
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=70, b=95),
                        )
                        fig.update_layout(xaxis_title="MÊS", yaxis_title="")

                        # ==================================================
                        # TÍTULOS DOS FACETS (UF):
                        # - limpa "COL=UF"
                        # - NÃO força todos para mesma posição
                        # - só aplica um SHIFT (ajustável)
                        # ==================================================
                        TITLE_SHIFT_Y = 0.035  # 👉 AUMENTE para descer | DIMINUA para subir
                        TITLE_FONT_SIZE = 13

                        for ann in fig.layout.annotations:
                            # limpa prefixo "COL=..."
                            if ann.text and "=" in ann.text:
                                ann.text = ann.text.split("=", 1)[1]

                            # ✅ mantém x/y original do facet e só desloca um pouco
                            ann.y = ann.y - TITLE_SHIFT_Y

                            ann.xanchor = "center"
                            ann.yanchor = "bottom"
                            ann.font = dict(size=TITLE_FONT_SIZE, color="white", family="Arial Black")

                        st.plotly_chart(fig, use_container_width=True)


# ==================================================
# 📌 DEMANDA x DEMANDAS (GERAL) — X vs RESTANTE
# ==================================================
with tab_demanda:
    st.subheader("📌 Demanda x Demandas (Geral) — DEMANDA SOLICITADA (X vs RESTANTE)")

    opt_tipo = st.radio(
        "Tipo de nota (somente neste relatório)",
        options=["Apenas AM", "Apenas AS", "AM + AS (todas)"],
        index=0,
        horizontal=True,
        key="demanda_tipo_filtro"
    )

    COL_DEMANDA_LOCAL = achar_coluna(df, ["DEMANDA SOLICITADA", "DEMANDA_SOLICITADA", "DEMANDA"])
    COL_TIPO_LOCAL    = achar_coluna(df, ["TIPO"])

    if COL_DEMANDA_LOCAL is None:
        st.warning("Coluna 'DEMANDA SOLICITADA' não encontrada.")
    elif COL_TIPO_LOCAL is None:
        st.warning("Coluna 'TIPO' não encontrada (preciso dela p/ filtrar AM/AS aqui).")
    else:
        base = df_periodo.copy().dropna(subset=[COL_DEMANDA_LOCAL]).copy()

        if base.empty:
            st.info("Sem dados no período.")
        else:
            # filtra tipo só aqui
            tipo = base[COL_TIPO_LOCAL].astype(str).str.upper().str.strip()
            if opt_tipo == "Apenas AM":
                base = base[tipo.str.contains(r"\bAM\b", na=False)].copy()
            elif opt_tipo == "Apenas AS":
                base = base[tipo.str.contains(r"\bAS\b", na=False)].copy()

            if base.empty:
                st.info("Sem dados para o filtro AM/AS selecionado.")
            else:
                if "_RES_" not in base.columns:
                    st.warning("Coluna interna '_RES_' não encontrada.")
                else:
                    base = classificar_resultado(base, "_RES_")
                    base = base[base["_CLASSE_"].isin(["PROCEDENTE", "IMPROCEDENTE"])].copy()

                    if base.empty:
                        st.info("Sem dados (após remover OUTROS).")
                    else:
                        base["DEMANDA"] = base[COL_DEMANDA_LOCAL].astype(str).str.upper().str.strip()
                        demandas_disp = sorted(base["DEMANDA"].dropna().unique().tolist())

                        if not demandas_disp:
                            st.info("Sem demandas válidas.")
                        else:
                            dem_x = st.selectbox("Escolha a demanda (X)", demandas_disp, index=0, key="dem_x_vs_all")
                            base["GRUPO"] = "RESTANTE"
                            base.loc[base["DEMANDA"] == dem_x, "GRUPO"] = f"X: {dem_x}"

                            tab = (
                                base.groupby(["GRUPO", "_CLASSE_"])
                                .size()
                                .reset_index(name="QTD")
                            )

                            # prepara para usar o mesmo plot (DIM = GRUPO)
                            tab = tab.rename(columns={"GRUPO": "DIM"})
                            grupos = [f"X: {dem_x}", "RESTANTE"]
                            ordem = grupos

                            fig = _plot_stack_with_pct_and_box_sem_outros(
                                tab,
                                x_title="GRUPO",
                                chart_title=f"📌 Demanda x Demandas — {dem_x} vs Restante ({opt_tipo})",
                                category_order=ordem,
                                box_x=1.18,
                                box_y=0.98,
                            )
                            st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 🧾 DEMANDA x DEMANDAS (UF) — "DEMANDA SOLICITADA"
# Padrão do seu dashboard:
# - Barras agrupadas por UF (NOTIFICADOS vs OUTRAS DEMANDAS) + TOTAL
# - QTD dentro das barras
# - % acima (alinhada por barra)
# - legenda embaixo
# - sem grid e sem eixo esquerdo
# - quadro de totais à direita (comentado p/ mover)
# ==================================================

with tab_demanda_uf:
    st.subheader("📌 Demanda x Demandas (UF) — DEMANDA SOLICITADA")

    # =========================
    # Helpers locais (não dependem do resto)
    # =========================
    def _col_ok_local(c):
        try:
            return c is not None and str(c).strip() != "" and c in df.columns
        except Exception:
            return False

    def _norm_txt(s):
        return s.astype(str).str.upper().str.strip()

    def _fmt_int(n: int) -> str:
        return f"{int(n):,}".replace(",", ".")

    # =========================
    # Colunas necessárias
    # =========================
    if not _col_ok_local(COL_ESTADO):
        st.warning("Coluna de UF/ESTADO não encontrada (COL_ESTADO).")
        st.stop()

    # Coluna de demanda solicitada (você disse: "DEMANDA SOLICITADA")
    COL_DEMANDA = None
    for c in df.columns:
        if str(c).strip().upper() == "DEMANDA SOLICITADA":
            COL_DEMANDA = c
            break

    if COL_DEMANDA is None:
        st.warning('Coluna "DEMANDA SOLICITADA" não encontrada.')
        st.stop()

    base = df.copy()
    base[COL_ESTADO] = _norm_txt(base[COL_ESTADO]).replace({"": None})
    base = base.dropna(subset=[COL_ESTADO]).copy()

    # =========================
    # Filtro UF (opcional)
    # =========================
    ufs_disp = ["TOTAL"] + sorted(base[COL_ESTADO].dropna().unique().tolist())
    uf_filtro = st.selectbox("Filtrar UF (opcional)", options=ufs_disp, index=0, key="dem_uf_filtro")
    if uf_filtro != "TOTAL":
        base = base[base[COL_ESTADO] == uf_filtro].copy()

    # =========================
    # Define classes:
    # - NOTIFICADOS = demanda solicitada (coluna DEMANDA SOLICITADA preenchida)
    # - OUTRAS DEMANDAS = resto (vazio/nulo)
    # Obs: se você tiver um critério melhor (ex: valor específico),
    #      eu adapto, mas assim já funciona na maioria das bases.
    # =========================
    dem = base[COL_DEMANDA]
    mask_notif = dem.notna() & (dem.astype(str).str.strip() != "")

    base["_CLASSE_"] = "OUTRAS DEMANDAS"
    base.loc[mask_notif, "_CLASSE_"] = "NOTIFICADOS"

    # =========================
    # Agrega por UF x CLASSE
    # =========================
    tab = (
        base.groupby([COL_ESTADO, "_CLASSE_"])
        .size()
        .reset_index(name="QTD")
    )

    if tab.empty:
        st.info("Sem dados para este relatório.")
        st.stop()

    classes = ["NOTIFICADOS", "OUTRAS DEMANDAS"]
    ufs = sorted(tab[COL_ESTADO].unique().tolist())

    # garante grid completo (2 classes por UF)
    grid = (
        pd.DataFrame({COL_ESTADO: ufs}).assign(_k=1)
        .merge(pd.DataFrame({"_CLASSE_": classes}).assign(_k=1), on="_k")
        .drop(columns="_k")
    )
    tab = grid.merge(tab, on=[COL_ESTADO, "_CLASSE_"], how="left").fillna({"QTD": 0})
    tab["QTD"] = tab["QTD"].astype(int)

    # TOTAL por UF
    tot_uf = tab.groupby(COL_ESTADO)["QTD"].sum().reset_index(name="TOTAL_UF")
    tab = tab.merge(tot_uf, on=COL_ESTADO, how="left")

    # % por UF (cada barra em relação ao total daquela UF)
    denom = tab["TOTAL_UF"].replace(0, 1)
    tab["PCT"] = (tab["QTD"] / denom * 100).round(1)

    # =========================
    # Gráfico (Padrão)
    # =========================
    fig_uf = px.bar(
        tab,
        x=COL_ESTADO,
        y="QTD",
        color="_CLASSE_",
        barmode="group",
        template="plotly_dark",
        category_orders={"_CLASSE_": classes, COL_ESTADO: ufs},
        color_discrete_map={
            "NOTIFICADOS": COR_PROC,        # verde (padrão)
            "OUTRAS DEMANDAS": COR_IMP,     # vermelho (padrão)
        },
    )

    # QTD dentro
    fig_uf.update_traces(
        texttemplate="%{y}",
        textposition="inside",
        insidetextanchor="middle",
        cliponaxis=False,
    )

    # -------------------------
    # % acima (alinhada por barra)
    # -------------------------
    max_y = int(tab["QTD"].max()) if not tab.empty else 0
    OFFSET_Y = max(1, int(max_y * 0.06))  # ↑ maior = mais acima

    # shift para barras agrupadas
    SHIFT_A = -18  # NOTIFICADOS (←)
    SHIFT_B = +18  # OUTRAS DEMANDAS (→)

    for _, r in tab.iterrows():
        if int(r["QTD"]) == 0:
            continue
        xshift = SHIFT_A if r["_CLASSE_"] == "NOTIFICADOS" else SHIFT_B
        fig_uf.add_annotation(
            x=r[COL_ESTADO],
            y=int(r["QTD"]) + OFFSET_Y,
            text=f'{float(r["PCT"]):.1f}%',
            showarrow=False,
            font=dict(size=12, color="white", family="Arial Black"),
            xanchor="center",
            yanchor="bottom",
            xshift=xshift,
        )

    # sem grid e sem eixo esquerdo
    fig_uf.update_xaxes(showgrid=False, ticks="")
    fig_uf.update_yaxes(showgrid=False, visible=False, ticks="", zeroline=False)

    # legenda embaixo
    LEGEND_Y = -0.22  # (↓) menor = mais baixo | maior = mais alto
    fig_uf.update_layout(
        legend=dict(orientation="h", y=LEGEND_Y, x=0, title_text=""),
        margin=dict(l=10, r=260, t=30, b=90),
        xaxis_title="",
        yaxis_title="",
    )

    # =========================
    # Quadro de totais à direita
    # =========================
    notif_total = int(tab.loc[tab["_CLASSE_"] == "NOTIFICADOS", "QTD"].sum())
    outras_total = int(tab.loc[tab["_CLASSE_"] == "OUTRAS DEMANDAS", "QTD"].sum())
    total_geral = notif_total + outras_total

    # >>> AJUSTE POSIÇÃO DO QUADRO <<<
    BOX_X = 1.14  # (->) maior = mais DIREITA | menor = mais ESQUERDA
    BOX_Y = 0.98  # (^) maior = mais CIMA    | menor = mais BAIXO

    fig_uf.add_annotation(
        xref="paper", yref="paper",
        x=BOX_X, y=BOX_Y,
        showarrow=False, align="left",
        bgcolor="rgba(0,0,0,0.45)",
        bordercolor="rgba(255,255,255,0.25)",
        borderwidth=1,
        borderpad=10,
        text=(
            f"<span style='color:{COR_PROC};font-size:13px'><b>■ NOTIFICADOS</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(notif_total)}</b></span><br><br>"
            f"<span style='color:{COR_IMP};font-size:13px'><b>■ OUTRAS DEMANDAS</b></span><br>"
            f"<span style='color:white;font-size:18px'><b>{_fmt_int(outras_total)}</b></span><br><br>"
            f"<span style='color:#fcba03;font-size:13px'><b>TOTAL</b></span><br>"
            f"<span style='color:#fcba03;font-size:20px'><b>{_fmt_int(total_geral)}</b></span>"
        )
    )

    st.plotly_chart(fig_uf, use_container_width=True)

    # =========================
    # Tabela (tipo a da imagem)
    # =========================
    piv = (
        tab.pivot_table(index=COL_ESTADO, columns="_CLASSE_", values="QTD", aggfunc="sum", fill_value=0)
        .reset_index()
    )
    if "NOTIFICADOS" not in piv.columns:
        piv["NOTIFICADOS"] = 0
    if "OUTRAS DEMANDAS" not in piv.columns:
        piv["OUTRAS DEMANDAS"] = 0

    piv["TOTAL"] = piv["NOTIFICADOS"] + piv["OUTRAS DEMANDAS"]
    den2 = piv["TOTAL"].replace(0, 1)
    piv["%NOTIFICADOS"] = (piv["NOTIFICADOS"] / den2 * 100).round(1)
    piv["%OUTRAS"] = (piv["OUTRAS DEMANDAS"] / den2 * 100).round(1)

    st.dataframe(piv, hide_index=True, use_container_width=True)



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
