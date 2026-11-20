"""Bounded English lexical records; morphology does not imply semantic scores."""
from dataclasses import asdict, dataclass
import gzip
import hashlib
import json
from pathlib import Path


class ImportLimitError(ValueError):
    pass


def bounded_text(value, name, maximum=8192):
    if type(value) is not str or not value or len(value) > maximum:
        raise ValueError(f'{name} requires nonempty bounded text')
    return value


def texts(values, name, maximum=64):
    if type(values) is not list or len(values) > maximum:
        raise ValueError(f'{name} requires a bounded text list')
    return tuple(bounded_text(value, name) for value in values)


@dataclass(frozen=True)
class Form:
    text: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Sense:
    glosses: tuple[str, ...]
    tags: tuple[str, ...]
    examples: tuple[str, ...]


@dataclass(frozen=True)
class Lexeme:
    record_id: str
    lemma: str
    pos: str
    senses: tuple[Sense, ...]
    forms: tuple[Form, ...]
    source: str

    @property
    def upos(self):
        return {'noun':'NOUN','verb':'VERB','adj':'ADJ','adv':'ADV','pron':'PRON',
                'prep':'ADP','conj':'CCONJ','det':'DET','interj':'INTJ','num':'NUM'}.get(self.pos)

    def degree_forms(self, degree):
        if degree not in ('positive','comparative','superlative'):
            raise ValueError('Select a grammatical degree')
        return tuple(form.text for form in self.forms if degree in form.tags)

    def as_dict(self):
        return asdict(self)


def normalize_entry(value, *, source, record_id=None):
    """Return one English lexeme or None; preserve ambiguity rather than merge senses."""
    bounded_text(source, 'Source identity', 1024)
    if type(value) is not dict:
        raise ValueError('Wiktextract entries require objects')
    if value.get('lang_code') != 'en':
        return None
    senses, forms = value.get('senses', []), value.get('forms', [])
    if type(senses) is not list or len(senses) > 256 or type(forms) is not list or len(forms) > 512:
        raise ImportLimitError('Lexical entry exceeds sense/form limits')
    normalized_senses=[]
    for sense in senses:
        if type(sense) is not dict:
            raise ValueError('Sense requires an object')
        examples=sense.get('examples', [])
        if type(examples) is not list or len(examples)>64 or any(type(e) is not dict for e in examples):
            raise ValueError('Examples require bounded objects')
        normalized_senses.append(Sense(texts(sense.get('glosses', []),'Glosses'),
            texts(sense.get('tags', []),'Sense tags'),
            tuple(bounded_text(e['text'],'Example') for e in examples if e.get('text'))))
    normalized_forms=[]
    for form in forms:
        if type(form) is not dict:
            raise ValueError('Form requires an object')
        normalized_forms.append(Form(bounded_text(form.get('form'),'Form',1024),texts(form.get('tags',[]),'Form tags')))
    digest=hashlib.sha256(json.dumps(value,ensure_ascii=True,sort_keys=True,allow_nan=False).encode()).hexdigest()
    return Lexeme(record_id or source+':'+digest, bounded_text(value.get('word'),'Lemma',1024),
        bounded_text(value.get('pos'),'Part of speech',128),tuple(normalized_senses),tuple(normalized_forms),source)


def iter_wiktextract(path, *, source, max_records=1000, max_bytes=8*1024*1024):
    """Scan at most max_records source rows; non-English rows count toward the bound."""
    if type(max_records) is not int or not 1<=max_records<=1000000 or type(max_bytes) is not int or max_bytes<1:
        raise ValueError('Select positive finite record/byte limits')
    path=Path(path)
    opener=gzip.open if path.suffix=='.gz' else open
    total=0
    with opener(path,'rb') as stream:
        for _ in range(max_records):
            raw=stream.readline(min(1024*1024,max_bytes-total)+1)
            if not raw: return
            total+=len(raw)
            if total>max_bytes or len(raw)>1024*1024:
                raise ImportLimitError('Wiktextract scan exceeded its byte/record budget')
            value=json.loads(raw.decode('utf-8'),parse_constant=lambda _value: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
            result=normalize_entry(value,source=source)
            if result is not None: yield result
