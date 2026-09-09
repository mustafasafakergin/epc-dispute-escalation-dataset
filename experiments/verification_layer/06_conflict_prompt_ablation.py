# =============================================================
# ADIM 5: EK KONTROL TESTI
#   C) Thinking KAPALI + 1500 token (uzunluk mu, thinking mi etkili?)
#   D) Thinking KAPALI + Celiski-Farkindaligi Prompt Eklentisi
# =============================================================

import sys, re, time
sys.path.insert(0, '/content/drive/MyDrive/Doktora_Tezi/')

from retrieve import retrieve
import rag_generate
from rag_generate import generate_answer, safe_category_filter, build_prompt as _original_build_prompt

from sentence_transformers import SentenceTransformer, util
embed_model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]

META_PATTERNS = [
    r'^(okay|let\'?s|first,? i need|i need to|now,? let|let me|so,? the)',
    r'\bthe user\b.*\b(is asking|mentioned|wants|provided)\b',
    r'^(tamam|şimdi|öncelikle|kullanıcı)',
]
def is_meta_commentary(sentence):
    s = sentence.lower().strip()
    return any(re.search(p, s) for p in META_PATTERNS)

def check_evidence_binding(generated_answer, retrieved_passages, threshold=0.55):
    sentences = split_into_sentences(generated_answer)
    if not sentences or not retrieved_passages:
        return []
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
    return [(m, "DOGRULANDI" if m in retrieved_gorus_no_list else "⚠️ UYDURULMUS_OLABILIR") for m in mentioned]

def contains_structured_output(text):
    has_yon = bool(re.search(r'\bYÖN\s*:', text, re.IGNORECASE))
    has_gerekce = bool(re.search(r'\bGEREKÇE\s*:', text, re.IGNORECASE))
    return has_yon, has_gerekce

def mentions_conflict(text):
    patterns = [r'çelişk', r'görüş ayrılığ', r'farklı yönde', r'tutarsız', r'ihtilaf']
    return any(re.search(p, text.lower()) for p in patterns)


def build_prompt_conflict_aware(query, retrieved):
    messages = _original_build_prompt(query, retrieved)
    ek_talimat = (
        "\n\nÖNEMLİ EK TALİMAT: Emsal kararlar arasında karar yönü bakımından "
        "bir ÇELİŞKİ veya GÖRÜŞ AYRILIĞI varsa, bunu yanıtının başında açıkça "
        "belirt (örn: 'Emsaller arasında görüş ayrılığı bulunmaktadır: ...'). "
        "Bu durumu görmezden gelip tek yönlü kesin bir cevap verme."
    )
    messages[-1]["content"] += ek_talimat
    return messages


def run_scenario(name, enable_thinking, max_new_tokens, sorgu, use_conflict_prompt=False):
    print("\n" + "#"*70)
    print(f"# SENARYO: {name}")
    print(f"# enable_thinking={enable_thinking}, max_new_tokens={max_new_tokens}, celiski_prompt={use_conflict_prompt}")
    print("#"*70)

    if use_conflict_prompt:
        rag_generate.build_prompt = build_prompt_conflict_aware
    else:
        rag_generate.build_prompt = _original_build_prompt

    t0 = time.time()
    sonuc = generate_answer(sorgu, k=3, enable_thinking=enable_thinking, max_new_tokens=max_new_tokens)
    elapsed = time.time() - t0

    print(f"\n[Süre: {elapsed:.1f} saniye]")
    print(f"\n--- MODEL YANITI (ilk 1200 karakter) ---")
    print(sonuc['response'][:1200])

    has_yon, has_gerekce = contains_structured_output(sonuc['response'])
    conflict_mentioned = mentions_conflict(sonuc['response'])
    print(f"\n[Kontrol] YÖN: {has_yon} | GEREKÇE: {has_gerekce} | Çelişki açıkça belirtildi mi: {conflict_mentioned}")

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

    print(f"[Doğrulama] Desteksiz: {n_unsupported}/{n_total} | Uydurma: {n_fabricated}/{len(ref_check)}")

    return {
        'name': name, 'elapsed': elapsed, 'has_yon': has_yon, 'has_gerekce': has_gerekce,
        'conflict_mentioned': conflict_mentioned,
        'n_unsupported': n_unsupported, 'n_total_sentences': n_total,
        'n_fabricated': n_fabricated, 'n_refs': len(ref_check),
    }


# =============================================================
sorgu = "Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"

results = []
results.append(run_scenario("C) Thinking KAPALI + 1500 token", enable_thinking=False, max_new_tokens=1500, sorgu=sorgu))
results.append(run_scenario("D) Thinking KAPALI + Çelişki-Farkındalığı Prompt", enable_thinking=False, max_new_tokens=512, sorgu=sorgu, use_conflict_prompt=True))

print("\n\n" + "="*75)
print("TAM KARŞILAŞTIRMALI TABLO (Önceki tur + Bu tur)")
print("="*75)
print(f"{'Senaryo':<42} {'Süre(s)':>8} {'Desteksiz':>10} {'Çelişki?':>9}")
print(f"{'A) Thinking KAPALI (512tok) [önceki]':<42} {75.3:>8.1f} {'0/8':>10} {'Hayır':>9}")
print(f"{'B) Thinking AÇIK (1500tok) [önceki]':<42} {195.2:>8.1f} {'5/44':>10} {'Hayır':>9}")
for r in results:
    print(f"{r['name']:<42} {r['elapsed']:>8.1f} {r['n_unsupported']}/{r['n_total_sentences']:>7} "
          f"{'Evet' if r['conflict_mentioned'] else 'Hayır':>9}")
