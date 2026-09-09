# Data Dictionary

Full variable definitions for `data/epc_dispute_dataset.csv` (645 rows, 16 columns).

| # | Column Name | Type | Description |
|---|---|---|---|
| 1 | `Vaka_ID` | ID (string) | Unique case identifier. Numeric IDs correspond to the original systematic collection; IDs prefixed `GAP###-###` correspond to cases added during targeted gap-filling rounds. |
| 2 | `Ulke_Bolge` | Categorical (~126 levels) | Country or region where the underlying project/dispute is located. |
| 3 | `Yil` | Numeric (year) | Year associated with the case (typically contract signing, dispute initiation, or first-instance filing — see `Uyusmazlik_Ozeti` for context; not fully standardized across cases). |
| 4 | `Proje_Sektoru_v4` | Categorical (16 levels) | Project sector: Karayolu/Otoyol (Highway), Kopru/Tunel (Bridge/Tunnel), Su/Atik Su/Baraj (Water/Wastewater/Dam), Fosil Yakit/Petrol-Gaz (Fossil Fuel/Oil-Gas incl. hydroelectric), Yenilenebilir Enerji (Renewable Energy), Madencilik (Mining), Havalimani (Airport), Liman/Deniz Altyapisi (Port/Marine Infrastructure), Hastane/Saglik (Hospital/Health), Egitim/Kampus (Education/Campus), Telekom/Veri Merkezi (Telecom/Data Center), Sanayi Tesisi/Fabrika (Industrial/Factory), Bina/Konut/Ticari (Building/Residential/Commercial), Nukleer Enerji (Nuclear), Demiryolu/Metro (Railway/Metro), Belirsiz/Veri Yetersiz (Undetermined/Insufficient Data). |
| 5 | `FIDIC_Kitap_Turu` | Categorical | Governing contract form (e.g., FIDIC Red/Yellow/Silver/Gold Book, or "FIDIC-dışı" [non-FIDIC] for other standard forms, national civil codes, or investment treaties). |
| 6 | `Atif_Maddeler` | Free text | Cited contractual clauses, statutory articles, or case/docket numbers referenced in the case. |
| 7 | `Kurum_Yargi_Yeri` | Free text / categorical | Deciding institution or forum (e.g., ICC arbitration, ICSID, national court and division). |
| 8 | `Uyusmazlik_Ozeti` | Free text | Summary of the dispute (truncated to ~200 characters in this export; fuller narratives available in the underlying research corpus). |
| 9 | `Claim_Turu` | Categorical, multi-label (semicolon-separated; 41 possible tags) | Claim type(s), e.g., Gecikme/EOT (Delay/Extension of Time), Degisiklik/Change Order, Fesih (Termination), Kalite/Kusur (Defects), Force Majeure, Odeme Uyusmazligi (Payment Dispute), Zemin Kosullari (Site Conditions), Teminat Mektubu (Performance Bond), DAB/Hakem Prosedur Usulsuzlugu (DAB/Arbitrator Procedure), Zamanasimi (Limitation), Tenfiz/Icra (Enforcement), Yatirim Anlasmasi Ihlali (BIT/ICSID) (Investment Treaty Breach), and others. "Siniflandirilmamis/Veri Yetersiz" indicates unclassified/insufficient data. |
| 10 | `Eskalasyon_Asamasi` | Ordinal categorical (9 levels) | Highest escalation stage reached, in ascending order: (1) Muhendis/Mimar Karari (Engineer's/Architect's Decision), (2) DAB/DAAB, (3) Arabuluculuk (Mediation), (4) Ilk Derece Tahkim (First-instance Arbitration), (5) Ilk Derece Devlet Mahkemesi (First-instance Court), (6) Hakem Karari Iptal Davasi (Award Annulment/Set-Aside), (7) Istinaf/Temyiz/Yuksek Mahkeme (Appeal/Cassation/Supreme Court), (8) Tenfiz/Icra (Enforcement), or "Belirsiz/Sadece Claim Asamasi" (Undetermined/Claim-stage only). |
| 11 | `Sonuc_Yonu` | Categorical | Outcome direction: Davaci Lehine (Claimant-favorable), Davali Lehine (Respondent-favorable), Yuklenici Lehine (Contractor-favorable), Isveren Lehine (Employer-favorable), Karma/Kismi (Mixed/Partial), Uzlasma (Settled), Devam Eden Dava (Ongoing), Bozma (Usul) (Procedural Remand), Belirsiz/Veri Yok (Undetermined — no outcome data in source), Belirsiz/Detay Sinirli (Undetermined — limited detail). |
| 12 | `Vaka_Adi` | Free text | Full case name/citation as it appears in the primary source. |
| 13 | `Kaynak` | Free text | Primary source of the case record (e.g., specific database, publication, or law firm bulletin). |
| 14 | `Karar_Yonu_Ham` | Free text | Raw/verbatim outcome text from the source document before categorization into `Sonuc_Yonu`. |
| 15 | `Tahmini_Tutar_USD` | Numeric (USD) | Estimated monetary value extracted via regex-based text mining from claim/award amounts mentioned in the case text. Approximately 15% coverage; values represent maximum monetary figure identified in the case narrative (may reflect claimed, awarded, or settled amounts — not consistently distinguished). |
| 16 | `Sure_Yil_Cikarilan` | Numeric (years) | Case duration extracted via multiple text-mining methods (explicit duration statements, contextual date-pair matching, min/max year span in case narrative, or ICSID/PCA case-number-derived filing year combined with award year). Approximately 23% coverage. **Caution**: methodology combines several extraction heuristics of varying reliability; see `docs/METHODOLOGY.md`. |

## Coding Notes

- **Missing values**: Represented as empty cells in the CSV. For `Proje_Sektoru_v4`, `Claim_Turu`, `Eskalasyon_Asamasi`, and `Sonuc_Yonu`, an explicit "Belirsiz/..." (Undetermined) category is used instead of blank, to distinguish "we looked and could not determine" from "not yet coded."
- **Language**: Column headers and category labels are in Turkish (the dataset's primary working language), reflecting the doctoral research context. An English translation table is provided above; English machine translation of free-text fields is straightforward but not provided pre-translated to preserve fidelity to original legal terminology.
- **Multi-label fields**: `Claim_Turu` may contain multiple semicolon-separated tags per case (e.g., "Gecikme/EOT; Odeme Uyusmazligi").
