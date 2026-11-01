import streamlit as st

from src.app_utils import documents_table, get_engine

engine = get_engine()
docs = documents_table(engine)


with st.container(key="card_sky_koleksi_1", horizontal=True, vertical_alignment="bottom"):
    kategori = st.pills("Kategori", sorted(docs["kategori"].dropna().unique()), selection_mode="multi",
                        key="kol_kategori")
    cari_judul = st.text_input("Filter judul", placeholder="contoh: tari", key="kol_judul")

view = docs
if kategori:
    view = view[view["kategori"].isin(kategori)]
if cari_judul.strip():
    view = view[view["judul"].str.contains(cari_judul.strip(), case=False, regex=False)]

st.caption(f"Menampilkan {len(view)} dari {len(docs)} dokumen")
st.dataframe(
    view, hide_index=True, height=560,
    column_config={
        "url": st.column_config.LinkColumn("url", display_text="buka artikel"),
        "jumlah_token": st.column_config.ProgressColumn(
            "jumlah token", format="%d", min_value=0, max_value=int(docs["jumlah_token"].max())),
    },
)
