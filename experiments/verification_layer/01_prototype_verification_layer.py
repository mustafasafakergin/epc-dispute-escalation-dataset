# =============================================================
# DOGRULAMA KATMANI (Verification Layer) — İlk Test Sürümü
# Mevcut RAG pipeline'ınızın (retrieve.py, rag_generate.py) üzerine eklenir
# =============================================================

# --- Bileşen 1: Kanıt Bağı Kontrolü (Evidence Binding Check) ---
from sentence_transformers import SentenceTransformer, util
import re

# Zaten yüklü olan embedding modelini tekrar kullanıyoruz
embed_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def split_into_sentences(text):
    """Basit cümle bölme (Türkçe için nokta/soru/ünlem bazlı)."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]

def check_evidence_binding(generated_answer, retrieved_passages, threshold=0.55):
    """
    Üretilen cevabın her cümlesini, getirilen (retrieved) pasajlarla karşılaştırır.
    Döndürür: [(cümle, en_yüksek_benzerlik, durum), ...]
    durum: SUPPORTED (>=threshold), PARTIAL (threshold-0.15 arası), UNSUPPORTED (<threshold-0.15)
    """
    sentences = split_into_sentences(generated_answer)
    if not sentences:
        return []

    sent_embeds = embed_model.encode(sentences, convert_to_tensor=True)
    passage_embeds = embed_model.encode(retrieved_passages, convert_to_tensor=True)

    results = []
    for i, sent in enumerate(sentences):
        similarities = util.cos_sim(sent_embeds[i], passage_embeds)[0]
        max_sim = float(similarities.max())
        if max_sim >= threshold:
            status = "SUPPORTED"
        elif max_sim >= threshold - 0.15:
            status = "PARTIAL"
        else:
            status = "UNSUPPORTED"
        results.append((sent, round(max_sim, 3), status))
    return results


# --- Bileşen 2: Kural Tabanlı Hukuk Denetçisi (Rule-Based Legal Checker) ---
def extract_legal_references(text):
    """Metinden karar no, tarih, madde referanslarını regex ile çıkarır."""
    refs = {
        'karar_no': re.findall(r'\b\d{4}[/-]\d{1,5}\b', text),           # örn: 2015/342, 2015-342
        'yil': re.findall(r'\b(19[5-9]\d|20[0-3]\d)\b', text),           # 1950-2039 arası yıllar
        'madde': re.findall(r'\bmadde\s*\d+\b|\bm\.\s*\d+\b', text, re.IGNORECASE),
        'kanun_no': re.findall(r'\b\d{3,5}\s*sayılı\b', text, re.IGNORECASE),
    }
    return refs

def verify_legal_references(generated_answer, source_text_pool):
    """
    Üretilen cevaptaki her referansın, kaynak metin havuzunda (retrieved
    passages'ların birleşimi) gerçekten geçip geçmediğini kontrol eder.
    """
    gen_refs = extract_legal_references(generated_answer)
    source_combined = ' '.join(source_text_pool)

    verification = {}
    for ref_type, values in gen_refs.items():
        verification[ref_type] = []
        for v in values:
            found = v in source_combined
            verification[ref_type].append((v, "DOGRULANDI" if found else "KAYNAKTA_YOK_SUPHELI"))
    return verification


# --- Bileşen 3: Çatışma Tespiti (Conflict Detection) ---
def detect_conflict(retrieved_metadata_list):
    """
    Getirilen kararların 'Sonuc_Yonu' (veya benzeri) alanlarını karşılaştırır.
    retrieved_metadata_list: [{'sonuc': 'Davaci Lehine', ...}, {'sonuc': 'Davali Lehine', ...}, ...]
    """
    sonuclar = [m.get('sonuc', 'Bilinmiyor') for m in retrieved_metadata_list]
    unique_sonuclar = set(s for s in sonuclar if s != 'Bilinmiyor')
    if len(unique_sonuclar) > 1:
        return True, unique_sonuclar
    return False, unique_sonuclar


# =============================================================
# TEST SENARYOSU — Örnek kullanım
# =============================================================

# ÖRNEK: rag_generate.py'nizden gelen bir çıktı olduğunu varsayalım
ornek_uretilen_cevap = """
Bu tür bir gecikme talebinde, Yüklenici'nin sözleşmenin 20. maddesine göre
bildirim yükümlülüğünü yerine getirmesi gerekir. 2018/456 sayılı YFK kararında
benzer bir durumda İdare lehine karar verilmiştir. Ancak force majeure iddiası
söz konusu olduğunda sonuç değişebilir.
"""

ornek_retrieved_pasajlar = [
    "Yüklenici, sözleşmenin 20. maddesi uyarınca gecikmeyi 28 gün içinde bildirmekle yükümlüdür. Bildirim yapılmadığından talep reddedilmiştir.",
    "2017/892 sayılı kararda, İdare'nin gecikmeden sorumlu tutulmasına karar verilmiştir.",
]

print("="*60)
print("1) KANIT BAĞI KONTROLÜ")
print("="*60)
evidence_results = check_evidence_binding(ornek_uretilen_cevap, ornek_retrieved_pasajlar)
for sent, sim, status in evidence_results:
    print(f"[{status:12s}] (benzerlik={sim}) {sent[:80]}...")

print()
print("="*60)
print("2) HUKUKI REFERANS DOĞRULAMA")
print("="*60)
ref_check = verify_legal_references(ornek_uretilen_cevap, ornek_retrieved_pasajlar)
for ref_type, results in ref_check.items():
    if results:
        print(f"{ref_type}:")
        for val, status in results:
            print(f"    {val}: {status}")

print()
print("="*60)
print("3) ÇATIŞMA TESPİTİ (örnek metadata ile)")
print("="*60)
ornek_metadata = [{'sonuc': 'Davali Lehine'}, {'sonuc': 'Davaci Lehine'}]
has_conflict, sonuclar = detect_conflict(ornek_metadata)
print(f"Çatışma var mı: {has_conflict}, Bulunan sonuçlar: {sonuclar}")
if has_conflict:
    print("  --> Sistem, tek yönlü cevap vermek yerine 'çelişkili emsal' uyarısı vermeli!")
