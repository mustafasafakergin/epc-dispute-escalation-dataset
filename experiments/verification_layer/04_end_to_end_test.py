# =============================================================
# ADIM 3: TAM UCTAN UCA TEST — rag_generate.py + Dogrulama Katmani
# =============================================================

import sys, re, torch
sys.path.insert(0, '/content/drive/MyDrive/Doktora_Tezi/')

from retrieve import retrieve
from rag_generate import generate_answer, build_prompt

# --- Dogrulama katmani fonksiyonlari ---
from sentence_transformers import SentenceTransformer, util

# NOT: rag_generate.py zaten Qwen3-4B'yi yukleyecek (GPU bellek kullanir).
# Embedding modelini AYRI bir kucuk model olarak tutuyoruz, cakismaz.
embed_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]

def check_evidence_binding(generated_answer, retrieved_passages, threshold=0.55):
    sentences = split_into_sentences(generated_answer)
    if not sentences or not retrieved_passages:
        return []
    sent_embeds = embed_model.encode(sentences, convert_to_tensor=True)
    passage_embeds = embed_model.encode(retrieved_passages, convert_to_tensor=True)
    results = []
    for i, sent in enumerate(sentences):
        similarities = util.cos_sim(sent_embeds[i], passage_embeds)[0]
        max_sim = float(similarities.max())
        status = "SUPPORTED" if max_sim >= threshold else ("PARTIAL" if max_sim >= threshold-0.15 else "UNSUPPORTED")
        results.append((sent, round(max_sim, 3), status))
    return results

def verify_gorus_no_references(generated_answer, retrieved_gorus_no_list):
    mentioned = re.findall(r'\b(?:19|20)\d{2}/\d{1,3}\b', generated_answer)
    verification = []
    for m in mentioned:
        found = m in retrieved_gorus_no_list
        verification.append((m, "DOGRULANDI" if found else "⚠️ UYDURULMUS_OLABILIR (retrieved icinde YOK)"))
    return verification

def detect_outcome_conflict(retrieved_results):
    yonler = [r.get('Karar Yönü (Kaba Tahmin - Doğrulanmalı)', 'Bilinmiyor') for r in retrieved_results]
    unique_yonler = set(y for y in yonler if y != 'Bilinmiyor')
    return len(unique_yonler) > 1, unique_yonler


# =============================================================
# GERCEK UCTAN UCA CALISTIRMA
# =============================================================

# Onceki testte celiski buldugumuz sorguyu kullanalim (daha zorlu bir test):
sorgu = "Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"

print("Model yükleniyor ve yanıt üretiliyor (birkaç dakika sürebilir)...")
sonuc = generate_answer(sorgu, k=3)

print("\n" + "="*60)
print("RAG_GENERATE.PY GERÇEK ÇIKTISI")
print("="*60)
print(f"Sorgu: {sonuc['query']}")
print(f"Kategori filtresi: {sonuc['category_filter_used']}")
print(f"\nKullanılan emsaller: {sonuc['retrieved']}")
print(f"\n--- MODEL YANITI ---\n{sonuc['response']}")

# Dogrulama icin, prompt'ta GERCEKTEN kullanilan metni yeniden olusturuyoruz
# (build_prompt ile ayni retrieve cagrisini tekrarliyoruz - ayni sonuclari verir)
from rag_generate import safe_category_filter
cat_filter = safe_category_filter(sorgu)
retrieved_full = retrieve(sorgu, k=3, category_filter=cat_filter)
if not retrieved_full:
    retrieved_full = retrieve(sorgu, k=3, category_filter=None)

# Prompt'ta kullanilan asil "kanit" metinleri (Yuklenici Talebi + Kurul Karari)
evidence_passages = [
    f"{r.get('Yüklenicinin Talebi (Çıkarılan)', '')} {r.get('Kurul Kararı (Çıkarılan)', '')}"
    for r in retrieved_full
]
retrieved_gorus_nos = [r.get('Görüş No', '') for r in retrieved_full]

print("\n" + "="*60)
print("1) KANIT BAĞI KONTROLÜ (Model yanıtı vs gerçek kullanılan emsal metinleri)")
print("="*60)
evidence_results = check_evidence_binding(sonuc['response'], evidence_passages)
for sent, sim, status in evidence_results:
    print(f"[{status:12s}] (benzerlik={sim}) {sent[:90]}")

print("\n" + "="*60)
print("2) GÖRÜŞ NO DOĞRULAMA (Model bir numaradan bahsettiyse gerçek mi?)")
print("="*60)
ref_check = verify_gorus_no_references(sonuc['response'], retrieved_gorus_nos)
if ref_check:
    for val, status in ref_check:
        print(f"  {val}: {status}")
else:
    print("  (Model yanıtında hiç Görüş No formatında referans bulunamadı)")

print("\n" + "="*60)
print("3) ÇATIŞMA TESPİTİ (getirilen emsaller arasında)")
print("="*60)
has_conflict, yonler = detect_outcome_conflict(retrieved_full)
print(f"Çatışma var mı: {has_conflict}")
print(f"Getirilen kararların yönleri: {yonler}")
if has_conflict:
    print("  ⚠️  Model, bu çelişkiyi yanıtında belirtti mi? Yukarıdaki 'MODEL YANITI'nı kontrol edin.")

print("\n" + "="*60)
print("ÖZET DEĞERLENDİRME")
print("="*60)
n_unsupported = sum(1 for _, _, s in evidence_results if s == "UNSUPPORTED")
n_fabricated = sum(1 for _, s in ref_check if "UYDURULMUS" in s)
print(f"Desteksiz cümle sayısı: {n_unsupported}/{len(evidence_results)}")
print(f"Şüpheli/uydurma referans sayısı: {n_fabricated}/{len(ref_check)}")
print(f"Emsal çelişkisi model tarafından ele alındı mı: [YANITI MANUEL KONTROL EDİN]")
