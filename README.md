EPC Dispute Escalation Dataset
An International Corpus of Construction/EPC Contract Disputes for Early-Warning Model Development
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)
![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22674695.svg)
Overview
This repository contains a curated dataset of 645 publicly documented construction/EPC (Engineering, Procurement, Construction) contract disputes, compiled from international arbitration awards (ICSID, ICC, LCIA, SIAC, PCA), court judgments (BAILII, national supreme courts), and investment treaty databases (UNCTAD ISDS Navigator, italaw).
The dataset was assembled as part of a doctoral research project at Istanbul Technical University (İTÜ), Department of Civil Engineering, developing an early warning model for dispute escalation in international EPC contracts using small language models (SLMs).
Motivation
Disputes in international EPC contracts rarely emerge suddenly; they typically evolve through a chain: variation/change order → claim → dispute → escalation → resolution. Existing literature has largely focused on (a) static contract-text classification (pre-award) or (b) retrospective, single-jurisdiction dispute-outcome prediction. This dataset supports a third direction: modeling the dynamic, multi-stage escalation process across jurisdictions, using cases governed predominantly by FIDIC and other international standard forms.
Dataset Structure
File	Description
`data/epc_dispute_dataset.csv`	Main dataset, 645 cases × 16 variables
`docs/DATA_DICTIONARY.md`	Full variable definitions and coding scheme
`docs/METHODOLOGY.md`	Data collection and coding methodology
Key Variables
Proje_Sektoru_v4 — Project sector (16 categories: Highway, Bridge/Tunnel, Water/Dam, Power, Renewable Energy, Mining, Airport, Port, Hospital, Education, Telecom, Industrial, Residential/Commercial, Nuclear, etc.)
Claim_Turu — Claim type (multi-label, 41 categories: Delay/EOT, Variation, Termination, Defects, Force Majeure, Payment Dispute, DAB Procedure, Investment Treaty Breach, etc.)
Eskalasyon_Asamasi — Escalation stage reached (9-level ordinal hierarchy: Engineer's Decision → DAB/DAAB → Mediation → First-Instance Arbitration → First-Instance Court → Annulment/Set-Aside → Appeal/Cassation → Enforcement)
Sonuc_Yonu — Outcome direction (Claimant/Contractor favor, Respondent/Employer favor, Mixed/Partial, Settled, Ongoing, etc.)
Sure_Yil_Cikarilan — Case duration in years (extracted from contract date to final resolution, where determinable)
Tahmini_Tutar_USD — Estimated monetary value in USD (extracted via text mining, ~15% coverage)
See `docs/DATA_DICTIONARY.md` for the complete list of all 16 variables.
Data Sources
Cases were compiled from the following publicly accessible sources:
ICSID Case Law Database (icsid.worldbank.org)
italaw.com
UNCTAD Investment Dispute Settlement Navigator
BAILII (British and Irish Legal Information Institute)
Howard Kennedy / Corbett & Co Table of FIDIC Cases
Christopher R. Seppälä's published commentaries on ICC awards (seppalaarbitration.com)
National court databases (e.g., Turkish Court of Cassation via sonkarar.com)
Academic and industry sources (Global Arbitration Review, JusMundi)
All cases are derived from publicly available, non-confidential judicial and arbitral decisions. No confidential project files or privileged legal opinions are included.
Statistical Properties
Preliminary distributional fitting (see `docs/METHODOLOGY.md` for details):
Monetary value: Log-normal distribution (μ≈19.1, σ≈2.9; KS test p=0.61, n=92)
Outcome direction: Beta distribution (p̂≈0.64 claimant-favorable; n=344)
Annual case frequency (2000–2025): Overdispersed relative to Poisson (suggesting Negative Binomial)
Escalation to arbitration/court (beyond claim stage): ~77% of cases (n=645)
Case duration: Mean ≈8.0 years, median 6.0 years (n=146, ~23% coverage) — notably longer than the general ICSID average (3.6–4.7 years per empirical literature), suggesting the corpus is skewed toward high-value, high-profile, longer-running disputes (a documented limitation; see Methodology).
Known Limitations
Sector classification: ~32% of cases remain unclassified due to source summaries (particularly legal-principle-focused commentaries) not specifying project type.
Duration data: Only ~23% of cases have extractable start/end dates; likely reflects genuine data scarcity in source summaries rather than extraction failure.
Publication bias: The corpus likely over-represents large, high-value, long-duration disputes relative to the true population of EPC disputes (most of which settle quickly at DAB/mediation level and are never publicly reported).
Citation
If you use this dataset, please cite:
```
Şafak, M.E. (2026). EPC Dispute Escalation Dataset: An International Corpus of
Construction/EPC Contract Disputes [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22674695
```
Permanent archive: https://doi.org/10.5281/zenodo.22674695
License
This dataset is released under CC BY 4.0. All underlying source documents (arbitral awards, court judgments) are matters of public record; this compilation and coding scheme represent original scholarly work.
Related Work
This dataset supports ongoing doctoral research at İTÜ:
> "An Early Warning Model for Dispute Escalation in International EPC Contracts Using Small Language Models" (Şafak, M.E., advisor: Doç. Dr. Gürkan Emre Gürcanlı)
Contact
Mustafa Ergin Şafak — İTÜ Structural Engineering Doctoral Program
