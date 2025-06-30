import pandas as pd

# "#" ile başlayan satırları atla
df = pd.read_csv("../data/PGS000020_hmPOS_GRCh38.txt", sep="\t", comment="#")

# Yeni ID oluştur: chrCHR_POS_REF_ALT formatında
df["variant_id"] =  df["hm_chr"].astype(str) + "_" + df["hm_pos"].astype(str) + "_" + df["other_allele"] + "_" + df["effect_allele"]

# Gerekli sütunları seç ve sırala
df_out = df[["variant_id", "effect_allele", "effect_weight"]]

# Çıktıyı yaz
df_out.to_csv("../data/PGS000020_hmPOS_GRCh38_scorefile.txt", sep="\t", index=False, header=False)
