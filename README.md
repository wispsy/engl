# Engl

Initial PyPI preview: **0.1.0a1**. Released behavior and current development are
tracked in [Wispsy Releases](https://github.com/orgs/wispsy/projects/31).

Independent English lexical, morphological and dependency records. Python 3.14+,
with no model or harness dependency in the core.

`normalize_entry` and `iter_wiktextract` preserve English lemmas, multiple senses,
glosses, examples and tagged forms from explicitly selected Wiktextract JSONL
(including gzip). Native POS is retained; `upos` maps known tags explicitly.
`degree_forms('comparative')` returns tagged forms without manufacturing intensity
or a universal good/bad score. Every record retains a source-qualified identity.

`parse_sentence` and `iter_conllu` read bounded gold CoNLL-U annotations. They
validate basic word IDs, one root, head references and cycles while retaining
multiword/empty-node/enhanced metadata. This is an annotated-tree reader, not an
automatic parser for unannotated English.

```python
from engl import iter_wiktextract, iter_conllu

# Caller-selected local sources; these calls never download data.
lexemes = iter_wiktextract('words.jsonl.gz', source='reviewed-wiktionary-snapshot', max_records=100)
sentences = iter_conllu('train.conllu', source='reviewed-ud-snapshot', max_sentences=20)
```

Limits bound source rows, lines, annotation sizes and total expanded bytes.
Non-English rows count against scan limits. Dataset provenance/rights and source
approval belong to the calling application. Keep original records and source
versions for traceability. No dictionary, model weights or external text ships
inside the package.

Optional commands reuse Expose Interface:

```sh
uv sync --extra cli
uv run engl lexicon words.jsonl.gz --source reviewed-snapshot --limit 10
uv run engl dependencies train.conllu --source reviewed-ud --limit 10
```

Run `PYTHONPATH=src python -m unittest discover -s tests`. CI qualifies wheel/source
installations on Linux/macOS/Windows. The
[Engl Project](https://github.com/orgs/wispsy/projects/29) and
[complete Hero plan](https://github.com/wispsy/wispsy/blob/main/docs/cohesion-block-b/IMPLEMENTATION_PLAN.md)
track semantic representations, approved curricula and later adapters.
