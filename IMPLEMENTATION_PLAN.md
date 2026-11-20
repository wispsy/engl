# Engl implementation plan

Engl owns independent English lexical, morphological, dependency and later
semantic representations. The
[complete Hero/Cohesion Block B plan](https://github.com/wispsy/wispsy/blob/main/docs/cohesion-block-b/IMPLEMENTATION_PLAN.md)
and [Engl Project](https://github.com/orgs/wispsy/projects/29) hold the shared
architecture, source policy and execution queue.

## ENGL-01 — bounded lexical and dependency foundations

Normalize English Wiktextract records without collapsing distinct senses.
Preserve lemma/native POS, known UD POS mappings, definitions/examples, tagged
forms and source identity. Comparative degree is distinct from polarity and
calibrated intensity. Unknown mappings stay unknown; no universal numeric word
scores are invented. Stream local gzip/JSONL under row/line/byte budgets.

Read existing CoNLL-U annotations with basic ID/root/head/cycle validation and
preserve multiword/empty/enhanced metadata. Bound sentence size and source reads.
Use the provided English EWT files for actual local import receipts, retaining
the original train/dev/test split and source rights. A data reader does not claim
to parse arbitrary English. Keep datasets outside Git and package artifacts.

Acceptance includes ambiguity/forms, strict bounded import, real local corpus
samples, invalid/cyclic trees, optional commands and installed source/wheel
profiles on declared platforms. Core import starts no model, network or store.

## ENGL-02 — semantic representations

Select syntax-backed simple clause, modifier, negation and comparison records.
Keep semantic relations explicit and preserve syntax/source provenance alongside
them. Represent uncertainty and sense ambiguity. Parser training, WordNet,
Wikidata or calibrated valence datasets require explicit source selection and
measured evaluation. Do not claim an authored grammar covers all English.

## Ecosystem boundaries

Thoughtformula owns neural/tokenizer/training mathematics. Hypnosis owns approved
corpus selection, curricula and training/evaluation jobs. Thoughtform owns model
identity and lineage. Backpack supplies optional persistent records. Parse MD
handles approved Markdown selections; Astree handles actual HTML boundaries.
Engl does not rebuild their engines or extend an HTML core into a dictionary.
Public source is authorized; dataset/model publication and new sources require
their concrete selections and retained provenance.
