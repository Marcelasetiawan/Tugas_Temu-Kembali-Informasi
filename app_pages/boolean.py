import pandas as pd
import streamlit as st

from src.app_utils import get_engine, search_box
from src.ui import steps_row

engine = get_engine()
EXAMPLES = ["toraja AND (ritual OR makam)", "wayang AND (kulit OR golek)", "senjata AND dayak AND NOT tari"]

with st.container(key="card_sky_boolean_1"):
    query = search_box("bool", "Query Boolean", EXAMPLES, placeholder="contoh: wayang AND (kulit OR golek)",
                       help="Operator ditulis huruf besar. Dua kata tanpa operator dianggap AND.")

if query.strip():
    parsed = engine.boolean.parse(query)
    postfix = engine.boolean.to_postfix(parsed)
    fmt = lambda toks: " ".join(t[1] if isinstance(t, tuple) else t for t in toks)
    result = engine.boolean.search(query)

    with st.container(horizontal=True):
        st.metric("Dokumen cocok", len(result), border=True)
        st.metric("Dari total", engine.index.N, border=True)
    with st.expander("Langkah pemrosesan query", icon=":material/functions:"):
        st.markdown(f"**Setelah prapemrosesan:** `{fmt(parsed)}`")
        st.markdown(f"**Notasi postfix (shunting-yard):** `{fmt(postfix)}`")
        terms = [t[1] for t in parsed if isinstance(t, tuple)]
        st.markdown("**Postings list setiap term:**")
        st.dataframe(pd.DataFrame([{"term": t, "DF": engine.index.df(t),
                                    "postings (10 pertama)": ", ".join(engine.index.postings(t)[:10])}
                                   for t in dict.fromkeys(terms)]), hide_index=True)

    if result:
        st.dataframe(
            pd.DataFrame({"doc_id": result,
                          "judul": [engine.docs.loc[d, "title"] for d in result],
                          "url": [engine.docs.loc[d, "url"] for d in result]}),
            hide_index=True,
            column_config={"url": st.column_config.LinkColumn("url", display_text="buka artikel")},
        )
    else:
        st.warning("Tidak ada dokumen yang memenuhi query Boolean ini.", icon=":material/search_off:")
else:
    steps_row([
        ("AND", "Kedua kata harus ada. Contoh: toraja AND makam."),
        ("OR", "Salah satu kata cukup. Contoh: kulit OR golek."),
        ("NOT", "Kata tidak boleh ada. Contoh: senjata AND NOT tari."),
        ("Kurung ( )", "Mengelompokkan. Contoh: wayang AND (kulit OR golek)."),
    ])
