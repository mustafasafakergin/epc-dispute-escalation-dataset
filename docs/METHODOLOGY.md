# Methodology

## Data Collection

Cases were compiled through a combination of:

1. **Systematic archival review** of published compilations, including:
   - Howard Kennedy / Corbett & Co "Table of FIDIC Cases" (multiple editions, 1974–2026)
   - Christopher R. Seppälä's published commentaries on ICC awards dealing with FIDIC contracts (seppalaarbitration.com), including "Extracts from ICC Arbitral Awards" series
   - Global Arbitration Review's "Investment Treaty Arbitration in the Construction Sector"

2. **Country/party-cluster targeted search** using the UNCTAD Investment Dispute Settlement (ISDS) Navigator, which provides structured per-country case listings including year of initiation and outcome — an efficient method for identifying related cases sharing a common respondent state or claimant nationality (e.g., Turkish contractors vs. Turkmenistan, Libya).

3. **National court database search** (e.g., sonkarar.com for Turkish Court of Cassation 6th Civil Chamber decisions), using targeted keyword combinations (e.g., "eser sözleşmesi" [work contract], "gecikme cezası" [delay penalty]).

4. **Individual case verification** via primary sources (jusmundi.com, italaw.com, BAILII, national court portals) to confirm dates, sectors, and outcomes for high-value or high-profile cases.

## Coding Process

Each case was manually reviewed and coded across 16 variables (see `DATA_DICTIONARY.md`). Sector and claim-type classification used an iterative keyword-based classifier, expanded over multiple rounds as new terminology patterns were identified in the corpus (see version history in project records). Full-text (rather than truncated-summary) matching was found to substantially improve classification completeness, particularly for large narrative case entries.

## Duration Extraction

Case duration (`Sure_Yil_Cikarilan`) was extracted using several complementary methods, prioritized by reliability:

1. Explicit textual statements of duration (e.g., "X yıl süren dava" / "X-year dispute")
2. Contextual date-pair matching (identifying years near contextual markers such as "signed"/"imzalandı" for start and "final award"/"nihai karar" for end)
3. Minimum/maximum year span across all years mentioned in the case narrative
4. For ICSID/PCA cases, the filing year embedded in the case number (e.g., ARB/17/23 → 2017) combined with the latest year mentioned in the narrative (typically the award or enforcement decision year)

**Important caveat**: An initial naive implementation of method 4 produced a logical error (treating the arbitration-filing year as the "start" rather than the underlying contract date), which was identified and corrected. Researchers extending this dataset should verify duration values against primary sources before using them as ground truth for precise duration modeling; the ~23% coverage achieved likely represents a genuine ceiling given source data scarcity (multiple independent extraction attempts across ~15 additional targeted searches yielded no further cases), not merely a limitation of the extraction method.

## Statistical Distribution Fitting

Distributions were fit using standard Python statistical libraries (`scipy.stats`):
- **Log-normal** (monetary values): fit via `scipy.stats.lognorm`, floc=0; goodness-of-fit assessed via Kolmogorov-Smirnov test
- **Beta** (outcome direction): parameters estimated using a Jeffreys-prior-adjusted approach (α = successes + 0.5×partial + 0.5; β = failures + 0.5×partial + 0.5)
- **Poisson/Negative Binomial** (annual case frequency, 2000–2025): dispersion ratio (variance/mean) computed to test Poisson assumption; ratio >1.5 taken as evidence for overdispersion favoring Negative Binomial

## Known Limitations (Detailed)

### Sector Classification Gap (~32%)
The largest single source of unclassified sectors is the "Corbett & Co Table" lineage of case summaries, which are edited from a legal-practitioner perspective (documenting procedural/legal holdings) rather than an engineering perspective, and frequently omit project-type information entirely. This was verified by directly reading multiple original award texts corresponding to "unclassified" entries — even the primary source documents (not just the secondary summary) often lack explicit project-type description when the legal issue at hand does not require it.

### Duration Data Gap (~77% missing)
Similarly, most case summaries — particularly short-form legal bulletin entries — report only a single date (e.g., decision date) without contract signing or dispute-initiation date, making duration calculation impossible from the available text.

### Publication/Selection Bias
The dataset's mean case duration (~8.0 years) is substantially longer than published general ICSID averages (3.6–4.7 years per a 2021 empirical study), but closely matches the reported average for disputes exceeding USD 1 billion in value (~8 years). This strongly suggests the corpus — being built from published legal commentary, law firm bulletins, and case-law databases — systematically over-represents large, complex, long-running, and thus more "newsworthy" or "citable" disputes, while under-representing the (likely much more numerous) smaller disputes resolved quickly at the Engineer's Decision or DAB stage without ever reaching public arbitration or court records. Users of this dataset for probability modeling should account for this selection effect, e.g., by treating estimated distributions as conditional on "cases that became sufficiently significant/contested to generate a public record," rather than as representative of the full population of EPC contract disputes.

## Comparison with Related Literature

For a comparison of this dataset's methodology and scope against related Turkish-language doctoral research using national (Yargıtay/YFK) case sources, see the project's accompanying literature review documentation (available on request / in the associated thesis).
