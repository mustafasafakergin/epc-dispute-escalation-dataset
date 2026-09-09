# =============================================================
# ADIM 2: Gercek Retrieve Verisiyle Dogrulama Katmani Entegrasyonu
# =============================================================

import sys, re
sys.path.insert(0, '/content/drive/MyDrive/Doktora_Tezi/')
from retrieve import retrieve

# --- Dogrulama katmani fonksiyonlari (verification_layer_test.py'den) ---
from sentence_transformers import SentenceTransformer, util

embed_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]

def check_evidence_binding(generated_answer, retrieved_passages, threshold=0.55):
    sentences = split_into_sentences(generated_answer)
    if not sentences:
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

def extract_gorus_no_references(text):
    """YFK 'Görüş No' formatına özel: YYYY/NN (örn: 2015/07)"""
    return re.findall(r'\b(19|20)\d{2}/\d{1,3}\b', text)

def verify_gorus_no_references(generated_answer, retrieved_gorus_no_list):
    """Uretilen cevapta gecen Gorus No'larin, GERCEKTEN getirilen (retrieved)
    kararlar arasinda olup olmadigini kontrol eder."""
    mentioned = re.findall(r'\b(?:19|20)\d{2}/\d{1,3}\b', generated_answer)
    verification = []
    for m in mentioned:
        found = m in retrieved_gorus_no_list
        verification.append((m, "DOGRULANDI (retrieved icinde var)" if found else "UYDURULMUS_OLABILIR (retrieved icinde YOK)"))
    return verification

def detect_outcome_conflict(retrieved_results):
    yonler = [r.get('Karar Yönü (Kaba Tahmin - Doğrulanmalı)', 'Bilinmiyor') for r in retrieved_results]
    unique_yonler = set(y for y in yonler if y != 'Bilinmiyor')
    return len(unique_yonler) > 1, unique_yonler


# =============================================================
# GERCEK SORGU ILE UCTAN UCA TEST
# =============================================================

sorgu = "Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"
retrieved = retrieve(sorgu, k=3)

print("="*60)
print(f"SORGU: {sorgu}")
print("="*60)
for r in retrieved:
    print(f"  [{r['_score']:.3f}] Görüş No: {r.get('Görüş No')} | Yön: {r.get('Karar Yönü (Kaba Tahmin - Doğrulanmalı)')}")

# Kanit havuzu: gercek karar metinleri
retrieved_texts = [r.get('Çıkarılan Metin', '') for r in retrieved]
retrieved_gorus_nos = [r.get('Görüş No', '') for r in retrieved]

# --- BURAYA rag_generate.py'nizin ciktisini koyacagiz ---
# Simdilik ELINIZLE bir "sanki LLM uretmis gibi" ornek cevap yazalim,
# rag_generate.py'yi paylastiginizda gercek cikti ile degistirecegiz:
ORNEK_URETILEN_CEVAP = """
[BURAYA rag_generate() fonksiyonunuzun gercek ciktisini yapistirin]
"""

print()
print("="*60)
print("1) KANIT BAĞI KONTROLÜ")
print("="*60)
if "[BURAYA" not in ORNEK_URETILEN_CEVAP:
    evidence_results = check_evidence_binding(ORNEK_URETILEN_CEVAP, retrieved_texts)
    for sent, sim, status in evidence_results:
        print(f"[{status:12s}] (benzerlik={sim}) {sent[:80]}...")

    print()
    print("="*60)
    print("2) GÖRÜŞ NO DOĞRULAMA")
    print("="*60)
    ref_check = verify_gorus_no_references(ORNEK_URETILEN_CEVAP, retrieved_gorus_nos)
    for val, status in ref_check:
        print(f"  {val}: {status}")
else:
    print("  (rag_generate.py ciktisi henuz eklenmedi - asagida talimat var)")

print()
print("="*60)
print("3) ÇATIŞMA TESPİTİ (gerçek retrieved kararlar arasında)")
print("="*60)
has_conflict, yonler = detect_outcome_conflict(retrieved)
print(f"Çatışma var mı: {has_conflict}")
print(f"Getirilen kararların yönleri: {yonler}")
if has_conflict:
    print("  ⚠️  UYARI: Getirilen emsaller birbiriyle çelişiyor!")
    print("      Sistem, kesin bir cevap yerine 'emsaller arasında görüş ayrılığı var' demeli.")
