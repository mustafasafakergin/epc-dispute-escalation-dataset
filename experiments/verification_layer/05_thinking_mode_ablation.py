# =============================================================
# ADIM 4: IKI SENARYOYU KARSILASTIRMALI TEST
#   A) enable_thinking=False (dusunme adimini atla)
#   B) enable_thinking=True + max_new_tokens=1500 (dusunmeye yer ac)
# =============================================================

import sys, re, torch, time
sys.path.insert(0, '/content/drive/MyDrive/Doktora_Tezi/')

from retrieve import retrieve
from rag_generate import generate_answer, safe_category_filter

from sentence_transformers import SentenceTransformer, util
embed_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]

# --- IYILESTIRME: Meta-yorum/dusunme cumlelerini filtrele ---
META_PATTERNS = [
    r'^(okay|let\'?s|first,? i need|i need to|now,? let|let me|so,? the)',
    r'\bthe user\b.*\b(is asking|mentioned|wants|provided)\b',
    r'^(tamam|şimdi|öncelikle|kullanıcı)',  # turkce meta-yorum varyantlari
]
def is_meta_commentary(sentence):
    s = sentence.lower().strip()
    return any(re.search(p, s) for p in META_PATTERNS)

def check_evidence_binding(generated_answer, retrieved_passages, threshold=0.55):
    sentences = split_into_sentences(generated_answer)
    if not sentences or not retrieved_passages:
        return []
    # Meta-yorumlari disarida tut
    sentences = [s for s in sentences if not is_meta_commentary(s)]
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

def verify_gorus_no_references(generated_answer, retrieved_gorus_no_list):
    mentioned = re.findall(r'\b(?:19|20)\d{2}/\d{1,3}\b', generated_answer)
    verification = []
    for m in mentioned:
        found = m in retrieved_gorus_no_list
        verification.append((m, "DOGRULANDI" if found else "⚠️ UYDURULMUS_OLABILIR"))
    return verification

def contains_structured_output(text):
    """YON: ve GEREKCE: basliklarinin gercekten uretilip uretilmedigini kontrol eder."""
    has_yon = bool(re.search(r'\bYÖN\s*:', text, re.IGNORECASE))
    has_gerekce = bool(re.search(r'\bGEREKÇE\s*:', text, re.IGNORECASE))
    return has_yon, has_gerekce


def run_scenario(name, enable_thinking, max_new_tokens, sorgu):
    print("\n" + "#"*70)
    print(f"# SENARYO: {name}")
    print(f"# enable_thinking={enable_thinking}, max_new_tokens={max_new_tokens}")
    print("#"*70)

    t0 = time.time()
    sonuc = generate_answer(sorgu, k=3, enable_thinking=enable_thinking, max_new_tokens=max_new_tokens)
    elapsed = time.time() - t0

    print(f"\n[Süre: {elapsed:.1f} saniye]")
    print(f"\n--- MODEL YANITI (ilk 1500 karakter) ---")
    print(sonuc['response'][:1500])
    print("..." if len(sonuc['response']) > 1500 else "")

    has_yon, has_gerekce = contains_structured_output(sonuc['response'])
    print(f"\n[Yapisal cikti kontrolu] YÖN: basligi var mi -> {has_yon} | GEREKÇE: basligi var mi -> {has_gerekce}")

    cat_filter = safe_category_filter(sorgu)
    retrieved_full = retrieve(sorgu, k=3, category_filter=cat_filter) or retrieve(sorgu, k=3, category_filter=None)
    evidence_passages = [
        f"{r.get('Yüklenicinin Talebi (Çıkarılan)', '')} {r.get('Kurul Kararı (Çıkarılan)', '')}"
        for r in retrieved_full
    ]
    retrieved_gorus_nos = [r.get('Görüş No', '') for r in retrieved_full]

    evidence_results = check_evidence_binding(sonuc['response'], evidence_passages)
    n_unsupported = sum(1 for _, _, s in evidence_results if s == "UNSUPPORTED")
    n_total = len(evidence_results)

    ref_check = verify_gorus_no_references(sonuc['response'], retrieved_gorus_nos)
    n_fabricated = sum(1 for _, s in ref_check if "UYDURULMUS" in s)

    print(f"\n[Doğrulama Özeti] Desteksiz cümle: {n_unsupported}/{n_total} | Uydurma referans: {n_fabricated}/{len(ref_check)}")

    return {
        'name': name, 'elapsed': elapsed, 'has_yon': has_yon, 'has_gerekce': has_gerekce,
        'n_unsupported': n_unsupported, 'n_total_sentences': n_total,
        'n_fabricated': n_fabricated, 'n_refs': len(ref_check),
        'response_length': len(sonuc['response']),
    }


# =============================================================
sorgu = "Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"

results = []
results.append(run_scenario("A) Thinking KAPALI", enable_thinking=False, max_new_tokens=512, sorgu=sorgu))
results.append(run_scenario("B) Thinking AÇIK + Genişletilmiş Token", enable_thinking=True, max_new_tokens=1500, sorgu=sorgu))

print("\n\n" + "="*70)
print("KARŞILAŞTIRMALI ÖZET TABLO")
print("="*70)
print(f"{'Senaryo':<35} {'Süre(s)':>8} {'YÖN?':>6} {'GEREKÇE?':>9} {'Desteksiz':>10} {'Uydurma':>8}")
for r in results:
    print(f"{r['name']:<35} {r['elapsed']:>8.1f} {str(r['has_yon']):>6} {str(r['has_gerekce']):>9} "
          f"{r['n_unsupported']}/{r['n_total_sentences']:>7} {r['n_fabricated']}/{r['n_refs']:>6}")
