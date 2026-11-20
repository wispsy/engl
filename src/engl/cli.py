"""Explicit optional Expose Interface inspection; does not download source data."""
from dataclasses import asdict
import json
import sys
from expose_interface import Interface
from . import iter_conllu, iter_wiktextract


def main(argv=None):
    app=Interface('engl',description='Inspect bounded English lexical/dependency records.')
    @app.command(name='lexicon')
    def lexicon(path:str,*,source:str,limit:int=10):
        return {'schema':1,'records':[asdict(v) for v in iter_wiktextract(path,source=source,max_records=limit)]}
    @app.command(name='dependencies')
    def dependencies(path:str,*,source:str,limit:int=10):
        return {'schema':1,'sentences':[asdict(v) for v in iter_conllu(path,source=source,max_sentences=limit)]}
    try:
        value=app.invoke(argv)
        if value is not None: print(json.dumps(value,ensure_ascii=True,allow_nan=False))
    except Exception as error:
        print(json.dumps({'schema':1,'error':type(error).__name__}),file=sys.stderr)
        raise SystemExit(1) from None
