---
Title: Versioning Convention
Status: Accepted
Last-reviewed: 2026-07-02
Related:
  - docs/00_Benchmark_Charter.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/08_Dataset_Specification.md
  - docs/11_Benchmark_Assurance.md
  - docs/conventions/decision-records.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
---

# Versioning Convention

*This convention defines the **process** by which specifications, code, and corpora are versioned,
released, and kept comparable. It is the file referenced by
[Label Specification §11](../06_Label_Specification.md) as the project versioning convention. It was
authored under work package V1-002 of the active release plan; BM approval under that work package
activates it, recorded by updating `Status:` (bookkeeping, not a convention change). The normative
semantics of versioning — what counts as a label-meaning change, what immutability means for a
released label, how versions are compared — are owned by the Label Specification (§§10–11), the
Benchmark Data Model (§9), the Dataset Specification (§§11, 17), and the Benchmark Assurance document
(§§6–9); where wording here and an owning specification differ, the owning specification governs.
What this convention **owns** is the process side: the version trains, tags, document metadata, and
the stamping obligation — the co-ownership that Formal Definitions §26 assigns it for the Corpus
Manifest (§5). It decides no open semantic question; see §9.*

## 1. Two version trains

The project runs **two independent version trains** (Data Model V1; Dataset Specification N11.1):

1. **Specification / code** — Semantic Versioning, `MAJOR.MINOR.PATCH`.
2. **Corpus** — frozen, numbered, **immutable** releases. A corpus version is never edited; a
   correction is a new corpus version (Label Specification §10; Dataset Specification N11.2).

The two trains are linked only through **stamping** (§5): every corpus release records exactly which
specification versions produced it.

Authority ordering between accepted ADRs and their owning specifications is governed separately by
ADR-007 / V1-007; this convention does not rank documents or alter that authority relation.

## 2. Specification / code train (Semantic Versioning)

For each versioned specification or code artifact:

- **MAJOR** — a backward-incompatible change to a definition: anything that changes what an existing
  artifact, term, or label *means*. A MAJOR change **requires an ADR**
  ([decision-records.md](decision-records.md)); where it touches a Charter §5 item, the Charter's
  superseding-ADR requirement applies as the Charter states it. MAJOR changes engage the Charter §4
  (v1/v2) and Charter §5 (extraordinary-justification) tests, consolidated in §4 of this convention.
- **MINOR** — an additive, backward-compatible extension that changes the meaning of nothing that
  already exists.
- **PATCH** — editorial clarification that changes no definition, no eligibility, no verdict, and no
  code behavior.

Each owning specification refines this scale for its own subject matter, and that refinement governs.
In particular, the **Label Specification §11** is the authority on which of its changes are
MAJOR/MINOR/PATCH — e.g. that adding a behavioural state, a label value, or a reason code is MAJOR,
and that re-partitioning reason codes is never MINOR. This convention does not restate or adjust that
classification. The classification of any concrete proposed change is made through the
change-classification gate and, where required, an ADR (release plan §2.2;
[decision-records.md](decision-records.md) §12) — never by this document in advance.

**Train membership and initial versions.**

- The train covers the documents of the exact normative set (enumerated at freeze in
  `normative_file_manifest.tsv`, release plan V1-030) and, once implementation begins, code artifacts.
- Accepted ADRs are **not** versioned; they are immutable records revised only by supersession
  ([decision-records.md](decision-records.md) §8). Conventions carry a status, not a SemVer stamp,
  and change through the classification gate (§8).
- The **Reproducibility/Implementation Profile (RIP)** versions under its own artifact contract, owned
  by work package V1-024; this convention does not pre-empt it. The release plan versions itself
  (`Plan-Version`) outside both trains.
- A document enters the train at the version its first freeze/release assigns (for the current
  program, the v1.0 freeze stamps the exact normative set as authorized by V1-032). Before a
  document's first accepted version, it carries `Status: Draft` and **nothing about it is comparable
  across revisions by promise** — the intent of the scaffolding proposal's pre-1.0 rule, retained
  here as process.

## 3. Corpus train (frozen numbered releases)

- Corpus versions are **frozen numbered releases**. Within a released corpus version, every label —
  value, reason code, and provenance — is immutable (Label Specification §10; Data Model §7; Dataset
  Specification N11.2).
- A correction of any kind is a **new corpus version with its own manifest**, never a mutation of a
  released one (Label Specification §10; Dataset Specification N11.2).
- A pipeline change that alters label *values* under the **same** label meaning yields a **new corpus
  version** on the same benchmark line; existing labels are superseded, not edited (Data Model V4).
- Instance identities are stable across corpus versions; a later version may re-issue an identity
  with a corrected label value, related by identity but compared only within its own version (Dataset
  Specification N17.5; Data Model R7/V5).

**Identifier grammar after v1.0 (deferred).** The initial corpus release identifier is fixed by the
active release plan: `benchmark-corpus-v1.0` (V1-054). How subsequent corpus version numbers increment
— for corrections versus additive same-line releases — is **not defined here**: it is deferred to work
package **V1-026** or another BM-classified version-metadata decision. No replacement numbering scheme
is invented in this convention. Whatever grammar is adopted there, the settled rules above are
unaffected, and compatibility between corpus versions is established by the **manifest and the
published compatibility statement** (Dataset Specification §17) — never inferred from the digits of a
version identifier. A label-meaning change is never expressed as an increment of any digit: it opens a
**new benchmark line** (§4) with its own identity.

## 4. Label-meaning changes and the Charter v1/v2 boundary (preserved)

The Charter's rules bind both trains and are preserved exactly as stated:

- **Charter §4 (v1/v2 test).** *Would existing labels change meaning?* A change to the label
  definition, the causal-intervention basis, the output-only information bound, or the construct scope
  is **v2 — a new benchmark**. A change that adds data, generators, splits, baselines, or metrics
  without redefining the label is a v1 amendment. When in doubt, it is v2: preserving comparability of
  released corpora outranks the convenience of amending in place.
- **Charter §5 (extraordinary justification).** Each §5 item is **presumed out of bounds**. Making
  such a decision — the items include changing the label definition or the intervention basis, which
  also triggers §4 — requires a superseding ADR that names the specific Charter clause it touches
  **and argues the case explicitly; absent that, the decision may not be taken.**

Consequences already fixed by the owning specifications, recorded here for one-stop reading:

- A change to what a label means is a **MAJOR** bump of the owning specification and is
  **presumptively a new benchmark line (v2)** — a new corpus line, not an in-place amendment (Label
  Specification §11; Data Model V3; Dataset Specification N11.4; Benchmark Assurance §9).
- A change classified v2 yields a **different benchmark line**, not a comparable version of the
  existing one (Dataset Specification N17.3; Data Model V3).
- A label's **meaning** is fixed by the Label Specification version stamped in the manifest; a label's
  **value** is fixed by the corpus version that carries it. The two are stamped separately (Data Model
  V2; Dataset Specification N11.3).

## 5. Manifest stamping

**Ownership.** Formal Definitions §26 assigns the Corpus Manifest jointly to the Dataset
Specification and this convention. The split is: the **Dataset Specification (§10)** owns the
manifest's required contents and contract; **this convention** owns the process obligation that the
two trains exist and that every release stamps the governing versions as follows.

- The **Corpus Manifest** (Formal Definitions §26) binds one corpus version to the exact specification
  versions (`05`/`06`/`06a`/`07`/`08`) that govern the meaning and production of its artifacts (Data
  Model V6; Dataset Specification N11.5, N10.3).
- Every corpus release records the Label Specification version under which its labels were produced;
  a label's meaning is read against that recorded version (Label Specification §11, Provenance).
- Each corpus release publishes a **compatibility statement** identifying which prior corpus versions
  it is, and is not, comparable to (Dataset Specification N17.2).
- Label values are compared only **within** a corpus version; cross-version comparison requires
  reading each version against its stamped specification versions (Data Model V5; Dataset
  Specification N17.1). Predictors and scorecards key their results to a specific corpus version
  (Dataset Specification N17.4).
- The **freeze manifest** (`freeze_manifest.sha256`, release plan §2.3) is release *evidence* — the
  hash inventory of the frozen specification set. It is distinct from the Corpus Manifest and does not
  substitute for corpus stamping.

## 6. Release identifiers and tags

Naming follows the active release plan, which fixes the v1.0 identifiers:

- **Specification freeze tag:** annotated `benchmark-spec-v1.0-freeze` on the internal freeze commit
  (release plan V1-032).
- **Public specification tag:** annotated `benchmark-spec-v1.0` on the packaging commit, created only
  after packaging checks pass; the freeze tag and the public tag are distinct (release plan V1-037 and
  §6).
- **Public corpus tag:** annotated `benchmark-corpus-v1.0` (release plan V1-054).

Later specification releases follow the same pattern (`benchmark-spec-vX.Y.Z[-freeze]`). Post-v1.0
corpus release identifiers follow the increment grammar adopted under §3's deferral, within the
`benchmark-corpus-v…` prefix the plan establishes. All release tags are annotated. The Repository
Scaffolding Proposal's shorter draft forms (`spec-vX.Y.Z`, `corpus-vX.Y`, §11.2) were proposals only
and are superseded by the plan's naming; no existing tag is renamed (none exists yet).

## 7. Document status and version metadata

Current recorded practice, which this convention documents without extending:

- Every governed document carries front matter with at least `Title`, `Status`, and `Last-reviewed`,
  plus `Related` links. Normative specifications currently carry `Status: Draft` pre-freeze; the
  Charter is `Accepted`.
- At specification freeze, each document in the exact normative set is set to `Status: Accepted` with
  Benchmark-Version `v1.0`, as authorized through V1-032, and its path/authority/status/version/hash
  are enumerated in `normative_file_manifest.tsv` (release plan §6 and V1-030).
- The **complete** per-document version-metadata scheme (field names, per-document SemVer stamps, and
  their verification) is closed by work packages **V1-026** and **V1-030**. This convention does not
  pre-empt those items; until they close, the trains and semantics above apply and the concrete
  metadata fields remain as recorded practice.

## 8. Versioning of decisions and conventions

- **ADRs are not versioned.** They are immutable, append-only records; revision happens by
  supersession ([decision-records.md](decision-records.md) §8).
- **Conventions (this directory) change only through the release plan §2.2 change-classification
  gate** (`Status:` and `Last-reviewed` bookkeeping excluded). An ADR is required only when an
  existing governing authority requires one or when the BM classifies the change as ADR-level
  ([decision-records.md](decision-records.md) §9). A convention change is process-level and never
  alters what a released label means.
- **The Charter** is amended only under its own §5 extraordinary-justification rule, via a superseding
  ADR naming the clause; Charter amendments are rare, ADR-backed, and dated (Charter §7).

## 9. What this convention deliberately does not decide

Open questions with named owners are left exactly where they are:

- **Reproducibility vs immutability interaction** — which fields must rebuild exactly versus within a
  tolerance, and adjudication of changed labels on rebuild (release plan V1-015; Benchmark Assurance
  BL5). This convention fixes no tolerance and no exact/tolerated field split. (Whether a rebuild
  difference *is* a correction is V1-015's question.)
- **Numerical thresholds of any kind** — the Assurance document fixes no numbers, and neither does
  this convention (Benchmark Assurance §8).
- **Corpus size floors and human-evaluation protocol** — excluded from v1 closure unless separately
  approved (release plan V1-026).
- **Post-v1.0 corpus increment grammar** — deferred to V1-026 or another BM-classified
  version-metadata decision (§3).
- **D1 terminology** (V1-008), **eligibility** (V1-004), **subject identity** (V1-005), **P6
  semantics** (V1-006), and **intervention methods** — owned by their decision packages; nothing in
  this convention constrains their outcomes.
- **RIP versioning** — owned by the RIP artifact contract, work package V1-024 (§2).
- **Publication of construction-internal artifacts** (Data Model Q2) and other open registry items —
  owned by their listed specifications and work packages.
