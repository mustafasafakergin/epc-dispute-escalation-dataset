# =============================================================
# ADIM 1: Once metadata yapisini kesfedelim
# (retrieve.py zaten Colab'da mevcut olmali - ayni klasorde)
# =============================================================

import sys
sys.path.insert(0, '/content/drive/MyDrive/Doktora_Tezi/')
from retrieve import retrieve, guess_category, guess_category_ml

# Gercek bir sorguyla deneme
ornek_sorgu = "Süre uzatımı talebinin geç değerlendirilmesi nedeniyle uğranılan zarar"
sonuclar = retrieve(ornek_sorgu, k=3)

print("="*60)
print("METADATA YAPISI (ilk sonucun tum alanlari)")
print("="*60)
if sonuclar:
    for key, value in sonuclar[0].items():
        deger_ozeti = str(value)[:100] if value else "(bos)"
        print(f"  {key}: {deger_ozeti}")
else:
    print("Sonuc bulunamadi - sorguyu kontrol edin.")

print()
print("="*60)
print(f"TOPLAM {len(sonuclar)} SONUC GETIRILDI")
print("="*60)
for i, r in enumerate(sonuclar):
    print(f"\n[Sonuc {i+1}] Skor: {r.get('_score', 0):.3f}")
    print(f"  Görüş No: {r.get('Görüş No', '?')}")
    print(f"  Konu Başlığı: {r.get('Konu Başlığı', '?')}")
