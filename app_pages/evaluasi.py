import streamlit as st

from src.app_utils import METHOD_LABELS, get_engine, get_evaluation, show_results
from src.ui import bar_chart

engine = get_engine()
queries, ev = get_evaluation()
COLS = ["P@5", "R@5", "F1@5", "P@10", "R@10", "F1@10"]


jenis = st.segmented_control("Jenis query", ["Semua", "umum", "pendek_spesifik"], default="Semua",
                             required=True, key="eval_jenis")
data = ev if jenis == "Semua" else ev[ev["jenis"] == jenis]
mean = data.groupby("metode")[COLS].mean()

# ---------------- KPI ----------------
for metode in ["TF-IDF", "BM25"]:
    st.markdown(f"**{'TF-IDF + Cosine' if metode == 'TF-IDF' else 'BM25'}**")
    other = "BM25" if metode == "TF-IDF" else "TF-IDF"
    with st.container(horizontal=True):
        for c in COLS:
            diff = mean.loc[metode, c] - mean.loc[other, c]
            st.metric(c, f"{mean.loc[metode, c]:.3f}", round(diff, 3) if abs(diff) > 1e-9 else 0,
                      help=f"Selisih terhadap {other}", border=True)

# ---------------- grafik per query ----------------
with st.container(key="card_sky_evaluasi_1"):
    metric = st.segmented_control("Metrik", COLS, default="F1@10", required=True, key="eval_metric")
    st.subheader(f"{metric} per query")
    order = {q: i for i, q in enumerate(queries["qid"])}
    bar_chart(data.sort_values("qid", key=lambda s: s.map(order))[["qid", "metode", metric]],
              x="qid", y=metric, color="metode", height=320)

# ---------------- tabel ----------------
with st.container(key="card_mint_evaluasi_2"):
    st.subheader("Tabel evaluasi per query")
    table = data.pivot(index=["qid", "query"], columns="metode", values=COLS)
    table.columns = [f"{m} {c}" for c, m in table.columns]
    order = {q: i for i, q in enumerate(queries["qid"])}
    table = table.reset_index().sort_values("qid", key=lambda s: s.map(order))
    st.dataframe(
        table, hide_index=True,
        column_config={c: st.column_config.ProgressColumn(c, format="%.2f", min_value=0, max_value=1)
                       for c in table.columns if "@" in c},
    )

# ---------------- detail query ----------------
with st.container(key="card_lavender_evaluasi_3"):
    st.subheader("Detail hasil per query")
    options = [f"{r.qid} – {r.query}" for r in queries.itertuples()]
    choice = st.selectbox("Pilih query", options, key="eval_query")
    q = queries.iloc[options.index(choice)]
    relevant = set(q["relevant"])
    st.caption(f"Kriteria relevansi: {q['kriteria_relevansi']} · {len(relevant)} dokumen relevan")
    left, right = st.columns(2)
    for col, (label, key) in zip([left, right], METHOD_LABELS.items()):
        with col:
            st.markdown(f"**{label}**")
            show_results(engine.search(q["query"], method=key, top_k=10), relevant=relevant)
