"""
Tahap 1 - Prapemrosesan.

Alur untuk setiap teks (dokumen maupun query):
    case folding -> normalisasi -> tokenisasi -> stopword removal
    -> stemming (Sastrawi, kecuali nama diri) -> stopword removal tahap 2

Modul ini juga menangani nilai kosong dan dokumen duplikat pada dataset.
"""

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

REQUIRED_COLUMNS = ["doc_id", "title", "url", "content", "crawl_date"]

# Stopword tambahan di luar daftar Sastrawi: kata fungsi/keterangan yang sering
# muncul di artikel tetapi tidak membedakan topik dokumen.
EXTRA_STOPWORDS = {
    "yg", "dgn", "nya", "pun", "lah", "kah", "juga", "akan", "telah", "sudah",
    "masih", "sangat", "lebih", "bahkan", "hingga", "sejak", "antara", "tersebut",
    "dapat", "bisa", "harus", "banyak", "salah", "satu", "biasanya", "kini", "kemudian",
}

# Stopword tahap 2: kata dasar umum yang baru terlihat setelah stemming
# (contoh: "menjadi" -> "jadi", "memiliki" -> "milik", "merupakan" -> "rupa").
STEM_STOPWORDS = {"jadi", "milik", "rupa", "kenal", "bagai", "lalu", "sebut", "laku", "punya"}

# Koreksi stemming: Sastrawi membuang akhiran "-kah"/"-lah" karena mengira partikel
# (seperti pada "apakah", "inilah"), padahal bagian dari kata dasar.
# Daftar ini berisi kata di koleksi yang terbukti salah di-stem.
STEM_OVERRIDES = {
    "menikah": "nikah",          # Sastrawi: "meni"
    "melangkah": "langkah",      # Sastrawi: "lang"
    "bertingkah": "tingkah",     # Sastrawi: "ting"
    "berumpun": "rumpun",        # Sastrawi: "rum"
    "belumlah": "belum",         # Sastrawi: "bum"
    "bungkah": "bungkah",        # Sastrawi: "bung"
    "mekkah": "mekkah",          # Sastrawi: "mek"
}

# Nama diri yang jarang muncul sehingga tidak tertangkap deteksi otomatis,
# tetapi akan rusak jika di-stem (contoh: "mentawai" -> "tawa").
EXTRA_PROPER_NOUNS = {"mentawai", "kutai", "maluku", "bali", "minang", "minangkabau"}


# ---------------------------------------------------------------------------
# Dataset: nilai kosong dan duplikat
# ---------------------------------------------------------------------------
def load_dataset(path):
    """Membaca CSV hasil Tugas 1, lalu menangani nilai kosong dan duplikat.

    Mengembalikan (DataFrame bersih, dict laporan pembersihan).
    """
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing}")

    report = {"Dokumen awal": len(df)}
    report["Nilai kosong per kolom wajib"] = df[REQUIRED_COLUMNS].isna().sum().to_dict()

    # title kosong diisi string kosong; dokumen tanpa content tidak bisa dicari -> dibuang
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["content"] = df["content"].fillna("").astype(str).str.strip()
    df = df[df["content"] != ""]
    report["Setelah buang content kosong"] = len(df)

    df = df.drop_duplicates(subset=["doc_id"])
    df = df.drop_duplicates(subset=["url"])
    df = df.drop_duplicates(subset=["content"])
    report["Setelah buang duplikat (doc_id, url, content)"] = len(df)

    return df.reset_index(drop=True), report


# ---------------------------------------------------------------------------
# Deteksi nama diri
# ---------------------------------------------------------------------------
def detect_proper_nouns(texts, min_count=3, min_ratio=0.9):
    """Kata yang di tengah kalimat hampir selalu diawali huruf kapital dianggap nama diri.

    Nama diri tidak di-stem karena Sastrawi salah memotongnya,
    contoh: "bali" -> "bal", "maluku" -> "malu", "minang" -> "mang".
    """
    cap_count, low_count = Counter(), Counter()
    for text in texts:
        for sentence in re.split(r"(?<=[.!?])\s+", str(text)):
            words = re.findall(r"[A-Za-z]+", sentence)
            for w in words[1:]:                      # kata pertama kalimat dilewati
                (cap_count if w[0].isupper() else low_count)[w.lower()] += 1

    proper = {
        w for w, c in cap_count.items()
        if len(w) >= 3 and c >= min_count and c / (c + low_count[w]) >= min_ratio
    }
    return proper | EXTRA_PROPER_NOUNS


# ---------------------------------------------------------------------------
# Preprocessor
# ---------------------------------------------------------------------------
class Preprocessor:
    """Pipeline prapemrosesan yang dipakai sama persis untuk dokumen dan query."""

    def __init__(self, proper_nouns=None, stem_cache_path=None):
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopwords = set(StopWordRemoverFactory().get_stop_words()) | EXTRA_STOPWORDS
        self.proper_nouns = set(proper_nouns or [])
        self.stem_cache_path = Path(stem_cache_path) if stem_cache_path else None
        self.stem_cache = {}
        if self.stem_cache_path and self.stem_cache_path.exists():
            self.stem_cache = json.loads(self.stem_cache_path.read_text(encoding="utf-8"))

    # 1. Case folding
    @staticmethod
    def case_folding(text):
        return str(text).lower()

    # 2. Normalisasi
    @staticmethod
    def normalize(text):
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")   # buang aksen/karakter non-ASCII
        text = re.sub(r"https?://\S+", " ", text)               # URL
        text = re.sub(r"['`]", "", text)                        # apostrof: ma'nene -> manene
        text = re.sub(r"[^a-z\s]", " ", text)                   # angka, tanda baca, simbol
        return re.sub(r"\s+", " ", text).strip()

    # 3. Tokenisasi
    @staticmethod
    def tokenize(text):
        return text.split()

    # 4. Stopword removal
    def remove_stopwords(self, tokens):
        return [t for t in tokens if t not in self.stopwords and len(t) >= 2]

    # 5. Stemming
    def stem(self, tokens):
        result = []
        for t in tokens:
            if t in self.proper_nouns:                  # nama diri tidak di-stem
                result.append(t)
                continue
            if t in STEM_OVERRIDES:                     # koreksi kesalahan Sastrawi
                result.append(STEM_OVERRIDES[t])
                continue
            if t not in self.stem_cache:
                self.stem_cache[t] = self.stemmer.stem(t)
            result.append(self.stem_cache[t])
        return result

    # 6. Stopword removal tahap 2
    def remove_stem_stopwords(self, tokens):
        return [t for t in tokens
                if t not in self.stopwords and t not in STEM_STOPWORDS and len(t) >= 2]

    def preprocess(self, text):
        """Teks mentah -> daftar term."""
        tokens = self.tokenize(self.normalize(self.case_folding(text)))
        tokens = self.stem(self.remove_stopwords(tokens))
        return self.remove_stem_stopwords(tokens)

    def steps(self, text):
        """Hasil setiap tahap, untuk ditampilkan sebagai contoh sebelum-sesudah."""
        s1 = self.case_folding(text)
        s2 = self.normalize(s1)
        s3 = self.tokenize(s2)
        s4 = self.remove_stopwords(s3)
        s5 = self.stem(s4)
        s6 = self.remove_stem_stopwords(s5)
        return {
            "0. Teks asli": text,
            "1. Case folding": s1,
            "2. Normalisasi": s2,
            "3. Tokenisasi": s3,
            "4. Stopword removal": s4,
            "5. Stemming": s5,
            "6. Stopword tahap 2": s6,
        }

    def save_cache(self):
        if self.stem_cache_path:
            self.stem_cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.stem_cache_path.write_text(
                json.dumps(self.stem_cache, ensure_ascii=False), encoding="utf-8"
            )


def preprocess_corpus(df, preprocessor, output_path=None):
    """Memproses judul + isi setiap dokumen. Menyimpan dataset_preprocessed.csv jika diminta."""
    df = df.copy()
    df["tokens"] = (df["title"] + " " + df["content"]).map(preprocessor.preprocess)
    df["jumlah_token"] = df["tokens"].map(len)
    preprocessor.save_cache()

    if output_path:
        out = df[["doc_id", "title", "url", "crawl_date"]].copy()
        if "kategori" in df.columns:
            out["kategori"] = df["kategori"]
        out["jumlah_token"] = df["jumlah_token"]
        out["tokens"] = df["tokens"].map(" ".join)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output_path, index=False, encoding="utf-8-sig")
    return df
