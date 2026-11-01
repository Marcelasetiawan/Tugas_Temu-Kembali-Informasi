"""
Tahap 6 - Mesin Pencari Sederhana.

Alur:  query -> prapemrosesan (sama dengan dokumen) -> ambil kandidat dari
       inverted index -> hitung skor (TF-IDF + cosine atau BM25) -> urutkan
       -> Top-k -> tampilkan peringkat, judul, URL, skor, dan snippet.

Menjalankan versi baris perintah (dari folder tugas2_ir):
    python -m src.search_engine
"""

import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

from src.bm25 import BM25
from src.boolean_retrieval import BooleanRetrieval
from src.indexing import InvertedIndex
from src.preprocessing import Preprocessor, detect_proper_nouns, load_dataset, preprocess_corpus
from src.tfidf_retrieval import TFIDFRetrieval

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "dataset_crawling_ir.csv"
PREPROCESSED_PATH = ROOT / "data" / "dataset_preprocessed.csv"
INDEX_PATH = ROOT / "index" / "inverted_index.json"
STEM_CACHE_PATH = ROOT / "index" / "stem_cache.json"

METHODS = {"bm25": "BM25", "tfidf": "TF-IDF + Cosine"}


class SearchEngine:
    def __init__(self, data_path=DATA_PATH, k1=1.2, b=0.75, verbose=True):
        log = print if verbose else (lambda *a, **k: None)

        self.df, self.clean_report = load_dataset(data_path)
        log(f"Dataset dimuat: {len(self.df)} dokumen")

        proper_nouns = detect_proper_nouns(self.df["content"])
        self.pre = Preprocessor(proper_nouns=proper_nouns, stem_cache_path=STEM_CACHE_PATH)
        self.df = preprocess_corpus(self.df, self.pre, output_path=PREPROCESSED_PATH)
        log(f"Prapemrosesan selesai: {self.df['jumlah_token'].sum()} token")

        docs = dict(zip(self.df["doc_id"], self.df["tokens"]))
        self.index = InvertedIndex().build(docs)
        self.index.save(INDEX_PATH)
        log(f"Inverted index: {len(self.index.vocabulary)} term")

        self.tfidf = TFIDFRetrieval(self.index)
        self.bm25 = BM25(self.index, k1=k1, b=b)
        self.boolean = BooleanRetrieval(self.index, self.pre)
        self.docs = self.df.set_index("doc_id")

    # ---------------- snippet ----------------
    def snippet(self, doc_id, query_terms, max_len=240):
        """Kalimat yang paling banyak memuat term query, beserta kata yang cocok."""
        content = self.docs.loc[doc_id, "content"]
        sentences = re.split(r"(?<=[.!?])\s+", content)
        targets = set(query_terms)

        best, best_hits, best_words = sentences[0], 0, []
        for sent in sentences:
            words = re.findall(r"[A-Za-z']+", sent)
            matched = [w for w in words if set(self.pre.preprocess(w)) & targets]
            if len(set(m.lower() for m in matched)) > best_hits:
                best, best_hits, best_words = sent, len(set(m.lower() for m in matched)), matched
        if len(best) > max_len:
            best = best[:max_len].rsplit(" ", 1)[0] + " ..."
        return best, sorted(set(best_words), key=str.lower)

    # ---------------- pencarian ----------------
    def search(self, query, method="bm25", top_k=10):
        """Mengembalikan dict berisi term query, jumlah kandidat, hasil Top-k, dan pesan."""
        terms = self.pre.preprocess(query)
        known = [t for t in terms if t in self.index.index]
        result = {
            "query": query, "method": METHODS.get(method, method), "terms": terms,
            "unknown_terms": [t for t in terms if t not in self.index.index],
            "n_candidates": len(self.index.candidates(known)), "results": [], "message": "",
        }

        if not query.strip():
            result["message"] = "Query kosong. Silakan masukkan kata kunci."
            return result
        if not terms:
            result["message"] = "Query hanya berisi stopword/simbol, tidak ada term yang bisa dicari."
            return result
        if not known:
            result["message"] = (f"Tidak ditemukan dokumen untuk query '{query}'. "
                                 f"Term {terms} tidak ada di koleksi.")
            return result

        retriever = self.bm25 if method == "bm25" else self.tfidf
        ranked = retriever.search(terms, top_k=top_k)
        if not ranked:
            result["message"] = f"Tidak ditemukan dokumen yang relevan untuk query '{query}'."
            return result

        for rank, (doc_id, score) in enumerate(ranked, start=1):
            snip, matched = self.snippet(doc_id, known)
            result["results"].append({
                "rank": rank, "doc_id": doc_id,
                "title": self.docs.loc[doc_id, "title"],
                "url": self.docs.loc[doc_id, "url"],
                "score": score, "snippet": snip, "matched": matched,
            })
        return result

    def rank_ids(self, query, method="bm25", top_k=None):
        """Hanya daftar doc_id hasil ranking (dipakai untuk evaluasi)."""
        retriever = self.bm25 if method == "bm25" else self.tfidf
        return [d for d, _ in retriever.search(self.pre.preprocess(query), top_k=top_k)]


# ---------------------------------------------------------------------------
# Antarmuka baris perintah (CLI)
# ---------------------------------------------------------------------------
# lebar tampilan mengikuti lebar terminal (70–100 karakter)
WIDTH = max(70, min(100, shutil.get_terminal_size((86, 24)).columns - 1))
USE_COLOR = sys.stdout.isatty()


def color(text, code):
    """Memberi warna ANSI (hanya jika keluaran ke terminal)."""
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def bold(t):   return color(t, "1")
def cyan(t):   return color(t, "96")
def yellow(t): return color(t, "93")
def green(t):  return color(t, "92")
def red(t):    return color(t, "91")
def dim(t):    return color(t, "90")


def boxed(lines):
    """Kotak berbingkai ganda untuk judul program."""
    inner = WIDTH - 4
    out = ["╔" + "═" * (WIDTH - 2) + "╗"]
    out += ["║ " + bold(cyan(line.center(inner))) + " ║" for line in lines]
    out.append("╚" + "═" * (WIDTH - 2) + "╝")
    return "\n".join(out)


def table(headers, rows, widths, align):
    """Tabel berbingkai garis tunggal. align: 'l' (kiri) atau 'r' (kanan) per kolom."""
    def cell(text, w, a):
        text = textwrap.shorten(str(text), width=w, placeholder="...") if len(str(text)) > w else str(text)
        return text.rjust(w) if a == "r" else text.ljust(w)

    def line(l, m, r):
        return l + m.join("─" * (w + 2) for w in widths) + r

    out = [line("┌", "┬", "┐"),
           "│" + "│".join(" " + bold(cell(h, w, a)) + " " for h, w, a in zip(headers, widths, align)) + "│",
           line("├", "┼", "┤")]
    for row in rows:
        out.append("│" + "│".join(" " + cell(v, w, a) + " " for v, w, a in zip(row, widths, align)) + "│")
    out.append(line("└", "┴", "┘"))
    return "\n".join(out)


def print_result(res):
    print("\n" + "━" * WIDTH)
    print(f" {bold('HASIL PENCARIAN')}  \"{yellow(res['query'])}\"")
    print(f" Metode   : {res['method']}")
    print(f" Term     : {', '.join(res['terms']) if res['terms'] else '-'}")
    print(f" Kandidat : {res['n_candidates']} dokumen memuat minimal satu term query")
    print("━" * WIDTH)

    if res["message"]:
        print(f"\n {red('✗')} {res['message']}")
        return

    title_w = WIDTH - 31
    rows = [[r["rank"], r["doc_id"], r["title"], f"{r['score']:.4f}"] for r in res["results"]]
    print(f"\n {bold(f'Top-{len(rows)} dokumen')} (diurutkan dari skor tertinggi)")
    print(table(["No", "Doc ID", "Judul", "Skor"], rows, [3, 6, title_w, 8], ["r", "l", "l", "r"]))

    print(f"\n {bold('Detail hasil')}")
    for r in res["results"]:
        rank, score = f"[{r['rank']}]", f"{r['score']:.4f}"
        print(f"\n {yellow(rank)} {bold(r['title'])}")
        print(f"     Skor  : {green(score)}   ({r['doc_id']})")
        print(f"     URL   : {dim(r['url'])}")
        wrapped = textwrap.wrap(r["snippet"], width=WIDTH - 14)
        for i, part in enumerate(wrapped):
            print(f"     {'Isi   :' if i == 0 else '       '} {part}")


# (query, penjelasan) — ditampilkan di awal dan saat pengguna mengetik "contoh"
EXAMPLES = [
    ("ritual pemakaman suku toraja", "query umum beberapa kata: Rambu Solo, makam tebing Lemo/Londa, Ma'nene"),
    ("alat musik bambu dari sunda", "kata 'dari' otomatis dibuang (stopword); hasil: angklung, calung"),
    ("tari topeng", "kesenian tari topeng dari Bali, Cirebon, dan daerah lain"),
    ("kain tenun tradisional", "kain tenun berbagai daerah: Baduy, Sambas, Gringsing, Maluku"),
    ("angklung", "query pendek & spesifik (satu kata) untuk satu jenis kesenian"),
    ("smartphone android", "contoh query di luar topik budaya: tidak ada dokumen yang cocok"),
]


def show_examples():
    print(f"\n {bold('Contoh query')} (ketik nomornya untuk langsung mencari):")
    for i, (q, note) in enumerate(EXAMPLES, start=1):
        print(f"   {yellow(str(i))}. {bold(q)}")
        print(f"      {dim(note)}")
    print(dim("   Tips: tulis kata kunci saja (huruf besar/kecil dan imbuhan tidak berpengaruh, "
              "misalnya 'tarian' = 'tari')."))


def ask_method():
    print(f"\n {bold('Pilih metode ranking:')}")
    print("   1. BM25 (disarankan)")
    print("   2. TF-IDF + Cosine Similarity")
    choice = input(" Pilihan [1/2, Enter = 1]: ").strip()
    return "tfidf" if choice == "2" else "bm25"


def ask_top_k():
    k = input(" Jumlah hasil / Top-k [Enter = 10]: ").strip()
    return int(k) if k.isdigit() and int(k) > 0 else 10


def main():
    if os.name == "nt":
        os.system("")                       # aktifkan warna ANSI di Command Prompt Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    print(boxed(["MESIN PENCARI BUDAYA INDONESIA", "Tradisi & Kesenian  ·  Indonesia Kaya"]))
    print(dim(" Menyiapkan dataset dan inverted index ..."))
    engine = SearchEngine(verbose=False)
    print(f" {green('✓')} Siap: {engine.index.N} dokumen · {len(engine.index.vocabulary):,} term".replace(",", "."))
    show_examples()
    print(dim("\n Ketik 'contoh' untuk melihat daftar contoh lagi, 'keluar' untuk berhenti (atau tekan Ctrl+C)."))

    try:
        while True:
            print("\n" + "─" * WIDTH)
            query = input(f" {bold('Masukkan query')} (nomor contoh / 'contoh' / 'keluar'): ").strip()
            if query.lower() in ("keluar", "exit", "quit"):
                break
            if query.lower() in ("contoh", "bantuan", "help"):
                show_examples()
                continue
            if query.isdigit() and 1 <= int(query) <= len(EXAMPLES):
                query = EXAMPLES[int(query) - 1][0]
                print(f" Query contoh: {yellow(query)}")
            if not query:
                print(f" {red('✗')} Query kosong. Silakan ketik kata kunci atau nomor contoh.")
                continue
            method = ask_method()
            top_k = ask_top_k()
            print_result(engine.search(query, method=method, top_k=top_k))
    except (KeyboardInterrupt, EOFError):   # Ctrl+C atau input ditutup
        print()
    print(f"\n {green('Program selesai. Terima kasih!')}")


if __name__ == "__main__":
    sys.exit(main())
