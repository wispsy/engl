"""Independent English lexical, morphological and dependency representations."""
from .lexicon import Form, ImportLimitError, Lexeme, Sense, iter_wiktextract, normalize_entry
from .dependency import Sentence, Token, iter_conllu, parse_sentence

__all__=['Form','ImportLimitError','Lexeme','Sense','Sentence','Token','iter_wiktextract','normalize_entry','iter_conllu','parse_sentence']


def main():
    from .cli import main as run
    return run()
