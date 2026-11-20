"""Validated CoNLL-U basic dependency trees, not an unannotated-text parser."""
from dataclasses import dataclass
from pathlib import Path
import re

from .lexicon import ImportLimitError

UPOS=frozenset('ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X'.split())


@dataclass(frozen=True)
class Token:
    token_id: int
    form: str
    lemma: str
    upos: str
    features: tuple[tuple[str,str], ...]
    head: int
    relation: str
    enhanced: str
    misc: str


@dataclass(frozen=True)
class Sentence:
    sentence_id: str
    text: str | None
    tokens: tuple[Token, ...]
    multiwords: tuple[tuple[str, ...], ...]
    empty_nodes: tuple[tuple[str, ...], ...]
    source: str


def parse_sentence(lines, *, source):
    if len(lines)>1024 or sum(len(line) for line in lines)>1024*1024:
        raise ImportLimitError('Sentence exceeds its finite annotation budget')
    metadata={}
    tokens=[];multiwords=[];empty=[]
    for line in lines:
        if line.startswith('#'):
            if ' = ' in line:
                key,value=line[1:].strip().split(' = ',1)
                if key in metadata: raise ValueError('Duplicate sentence metadata')
                metadata[key]=value
            continue
        columns=line.split('\t')
        if len(columns)!=10:
            raise ValueError('CoNLL-U requires ten columns')
        identity,form,lemma,upos,_xpos,features,head,relation,enhanced,misc=columns
        if re.fullmatch(r'[1-9][0-9]*-[1-9][0-9]*',identity):
            left,right=map(int,identity.split('-'))
            if left>=right: raise ValueError('Invalid multiword token range')
            multiwords.append(tuple(columns));continue
        if re.fullmatch(r'[1-9][0-9]*\.[1-9][0-9]*',identity):
            empty.append(tuple(columns));continue
        if not identity.isascii() or not identity.isdigit() or not head.isascii() or not head.isdigit() or upos not in UPOS:
            raise ValueError('Invalid basic token identity/head/POS')
        pairs=[]
        if features!='_':
            for feature in features.split('|'):
                if '=' not in feature: raise ValueError('Invalid morphological feature')
                key,value=feature.split('=',1)
                if not key or not value or key in dict(pairs): raise ValueError('Invalid or duplicate feature')
                pairs.append((key,value))
        tokens.append(Token(int(identity),form,lemma,upos,tuple(pairs),int(head),relation,enhanced,misc))
    if not tokens or len(tokens)>512 or [t.token_id for t in tokens]!=list(range(1,len(tokens)+1)):
        raise ValueError('Basic word IDs must be a bounded contiguous sequence')
    heads={t.token_id:t.head for t in tokens}
    if sum(t.head==0 for t in tokens)!=1 or any((t.head==0)!=(t.relation=='root') for t in tokens):
        raise ValueError('A basic sentence requires exactly one declared root')
    for token in tokens:
        seen=set();cursor=token.token_id
        while cursor:
            if cursor in seen or cursor not in heads: raise ValueError('Dependency cycle or missing head')
            seen.add(cursor);cursor=heads[cursor]
    for row in multiwords:
        left,right=map(int,row[0].split('-'))
        if right>len(tokens): raise ValueError('Multiword range references missing words')
    for row in empty:
        if int(row[0].split('.')[0])>len(tokens): raise ValueError('Empty node references missing word')
    return Sentence(metadata.get('sent_id',''),metadata.get('text'),tuple(tokens),tuple(multiwords),tuple(empty),source)


def iter_conllu(path, *, source, max_sentences=1000, max_bytes=8*1024*1024):
    if type(max_sentences) is not int or not 1<=max_sentences<=1000000 or type(max_bytes) is not int or max_bytes<1:
        raise ValueError('Select positive finite sentence/byte limits')
    lines=[];total=0;count=0
    with Path(path).open('rb') as stream:
        while True:
            raw=stream.readline(65537)
            if not raw:
                if lines: yield parse_sentence(lines,source=source)
                return
            total+=len(raw)
            if total>max_bytes or len(raw)>65536:
                raise ImportLimitError('CoNLL-U scan exceeded its byte/line budget')
            line=raw.decode('utf-8').rstrip('\r\n')
            if not line:
                if lines:
                    yield parse_sentence(lines,source=source)
                    count+=1;lines=[]
                    if count>=max_sentences: return
            else:
                lines.append(line)
                if len(lines)>1024: raise ImportLimitError('Sentence has too many rows')
