# Migration / Vendor-Exit / Repatriation Cases (Seed Catalogue)

Outcome-side seed data for the FDK lock-in **deltaR^2** validation. Each row is a publicly
documented case where an organisation left (or tried to leave, or was forced out of, or
deliberately avoided) a vendor/cloud/platform. Compiled 2026-06-19 with web access.

> **This is a SEED catalogue, not a validated dataset.** Many outcome fields are `null`.
> Figures are cited where a public source exists; otherwise marked low-confidence and flagged
> `recollection, verify`. Do not run a headline statistic off this file.

## Cases

| case | org | from -> to | year | cost (USD) | dur (mo) | outcome | lock-in incident | lockin hint | conf |
|---|---|---|---|---|---|---|---|---|---|
| dropbox-magic-pocket | Dropbox | AWS S3 -> own DCs | 2015 | null (~$75M *saved*) | 30 | success | none (voluntary) | 0.70 | high |
| 37signals-cloud-exit | 37signals | AWS -> owned Dell/colo + Pure | 2022 | $700k hw | 18 | success | ~$250k S3 egress bill (waived) | 0.55 | high |
| geico-cloud-repatriation | GEICO | Azure -> OpenStack private | 2024 | null | null | ongoing | ~2.5x cost overrun, >$300M/yr | 0.75 | medium |
| x-twitter-sacramento-exit | X (Twitter) | own DC + AWS/GCP -> consolidated DC | 2023 | null | null | partial | ~$510M/5.5yr AWS take-or-pay | 0.60 | medium |
| ahrefs-stayed-off-cloud | Ahrefs | (vs AWS) -> colo owned hw | 2020 | $122M (6yr spend) | 72 | success | none (avoided) | 0.10 | high |
| parler-aws-deplatforming | Parler | AWS -> forced scramble | 2021 | null | null | **failure** | **forced suspension, days offline** | 0.85 | high |
| beeks-group-vmware-exit | Beeks Group | VMware -> OpenNebula | 2024 | null | null | success | ~1,000% VMware price hike | 0.65 | medium |
| vmware-broadcom-cohort | VMware customers (agg) | VMware -> various | 2024 | null | null | ongoing | 800-1,500% hikes; C&D; lawsuits | 0.80 | medium |
| oracle-java-per-employee | Oracle Java SE (agg) | Oracle JDK -> OpenJDK | 2023 | null | null | ongoing | per-employee 3-10x; audit pipeline | 0.70 | medium |
| snap-multi-cloud-commit | Snap | (single) -> ~$2B GCP + ~$1B AWS | 2017 | null | null | partial | take-or-pay cloud commitments | 0.60 | low |
| gitlab-stayed-on-cloud | GitLab | (considered) -> stayed on GCP | 2017 | null | null | success | none (deliberate stay) | 0.40 | low |
| basecamp-pre-cloud-baseline | 37signals (earlier) | own hw -> cloud -> reversed | 2019 | null | null | partial | none | 0.30 | low |
| stack-overflow-on-prem | Stack Overflow | (vs cloud) -> own/colo | 2018 | null | null | success | none (avoided) | 0.15 | low |
| broadcom-siemens-litigation | Siemens US | VMware -> disputed | 2025 | null | null | unknown | Broadcom litigation over usage | 0.80 | low |
| vmware-broadcom-eu-watchdog | EU VMware customers | VMware -> regulatory remedy | 2025 | null | null | ongoing | up to ~1,500% EU hikes | 0.80 | medium |
| generic-cloud-repatriation-cohort | CIO survey aggregate | cloud -> on-prem | 2024 | null | null | ongoing | cost overruns (survey stat) | 0.50 | low |

**16 cases.** Cited cost figures: **3** (Dropbox ~$75M saved, 37signals $700k hardware,
Ahrefs $122M 6yr spend) — and even those are savings/spend numbers, not clean migration costs.
The other 13 carry `migration_cost_usd: null`.

## Honest notes

**(a) Why this is a seed, not a dataset.** Every row here was selected *because it was written
about*. The fields that the deltaR^2 test actually needs — true migration cost, calendar duration
from decision to cutover, and a clean success/partial/failure label — are mostly unavailable.
What gets published is a headline savings number (often a *projection*, often from the party
that made the decision and has an incentive to look smart) rather than a fully-costed before/after.
Dropbox's ~$75M is a reduction in operating cost over two years, not the cost of Magic Pocket;
37signals' $700k is hardware spend, not the loaded cost of the move including engineering time.
Treat `migration_cost_usd` and `duration_months` as mostly missing, not as measured.

**(b) Selection bias is severe and runs one direction.** Famous exits are over-reported and
routine successful *stays* are invisible. A company that quietly renewed its cloud contract,
or migrated off a vendor without drama, generates no blog post and no trade-press coverage. The
loud cases skew toward (i) charismatic founders who blog (DHH), (ii) eye-watering numbers
(Ahrefs' $400M, GEICO's $300M/yr), and (iii) conflict (VMware/Broadcom, Oracle audits, Parler).
That means the catalogue over-represents high-lock-in, high-drama situations and under-represents
the modal outcome (boring, partial, or "we decided to stay"). The `gitlab-stayed-on-cloud`,
`stack-overflow-on-prem`, and `generic-cloud-repatriation-cohort` rows are included precisely to
keep at least a few non-exit / non-success / aggregate points in view, but they cannot
counterbalance the structural bias on their own. `est_lockin_score_hint` is an author prior, not
a measurement, and should never be used as a feature and an outcome at the same time.

**(c) What real validation would require.** A defensible deltaR^2 test needs a *representative
sample* with *measured* outcomes, not a curated anecdote list. Concretely: a sampling frame
(e.g. all firms above some size in a sector, or a panel of contracts), outcomes recorded
prospectively or from primary records (invoices, change tickets, contract terms) rather than
press narratives, an explicit definition of "success" fixed before scoring, and inclusion of the
silent cases — the stays, the abandoned-mid-migration, the ones nobody wrote about. Until then,
this file is useful for *building and sanity-checking* the lock-in feature and for qualitative
face-validity (do high-lock-in cases like VMware/Oracle/Parler actually look harder to exit?),
but any quantitative deltaR^2 computed on these 16 rows is illustrative only and must not be
reported as evidence that the FDK lock-in predictor works.
