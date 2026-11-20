from dataclasses import FrozenInstanceError
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from engl import ImportLimitError, iter_conllu, iter_wiktextract, normalize_entry, parse_sentence

ENTRY={'word':'good','lang_code':'en','pos':'adj','senses':[{'glosses':['Of high quality.']},{'glosses':['Suitable.'],'tags':['context']}],
       'forms':[{'form':'better','tags':['comparative']},{'form':'best','tags':['superlative']}]}
SENTENCE=['# sent_id = example','# text = The cat runs.',
 '1\tThe\tthe\tDET\t_\tDefinite=Def\t2\tdet\t_\t_',
 '2\tcat\tcat\tNOUN\t_\tNumber=Sing\t3\tnsubj\t_\t_',
 '3\truns\trun\tVERB\t_\tTense=Pres\t0\troot\t_\tSpaceAfter=No',
 '4\t.\t.\tPUNCT\t_\t_\t3\tpunct\t_\t_']


class EnglishTests(unittest.TestCase):
    def test_ambiguity_and_degree_are_preserved_without_numeric_scores(self):
        value=normalize_entry(ENTRY,source='authored-fixture/1')
        self.assertEqual(len(value.senses),2)
        self.assertEqual(value.upos,'ADJ')
        self.assertEqual(value.degree_forms('comparative'),('better',))
        self.assertEqual(value.degree_forms('superlative'),('best',))
        with self.assertRaises(FrozenInstanceError): value.lemma='changed'
        self.assertIsNone(normalize_entry({**ENTRY,'lang_code':'fr'},source='fixture'))

    def test_gzip_import_filtering_identity_and_byte_bounds(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'entries.jsonl.gz'
            with gzip.open(path,'wt') as stream:
                for value in (ENTRY,{**ENTRY,'lang_code':'fr'},ENTRY): stream.write(json.dumps(value)+'\n')
            values=list(iter_wiktextract(path,source='fixture',max_records=2))
            self.assertEqual(len(values),1)
            self.assertEqual(values[0].record_id,normalize_entry(ENTRY,source='fixture').record_id)
            with self.assertRaises(ImportLimitError): list(iter_wiktextract(path,source='fixture',max_bytes=5))

    def test_dependency_root_features_and_surface_metadata(self):
        value=parse_sentence(SENTENCE,source='fixture')
        self.assertEqual(value.tokens[2].head,0)
        self.assertEqual(value.tokens[1].features,(('Number','Sing'),))
        self.assertEqual(value.text,'The cat runs.')
        rows=SENTENCE[:2]+['1-2\tThecat\t_\t_\t_\t_\t_\t_\t_\t_']+SENTENCE[2:]+['2.1\tit\tit\tPRON\t_\t_\t_\t_\t3:nsubj\t_']
        value=parse_sentence(rows,source='fixture')
        self.assertEqual(len(value.multiwords),1)
        self.assertEqual(len(value.empty_nodes),1)

    def test_cycles_missing_heads_roots_and_fields_fail(self):
        for replacement in ('1\tThe\tthe\tDET\t_\t_\t1\tdet\t_\t_',
                            '1\tThe\tthe\tDET\t_\t_\t99\tdet\t_\t_',
                            '1\tThe\tthe\tDET\t_\t_\t0\troot\t_\t_', 'bad'):
            rows=list(SENTENCE);rows[2]=replacement
            with self.assertRaises(ValueError): parse_sentence(rows,source='fixture')

    def test_conllu_iteration_is_bounded(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/'sample.conllu'
            path.write_text('\n'.join(SENTENCE)+'\n\n'+'\n'.join(SENTENCE)+'\n')
            self.assertEqual(len(list(iter_conllu(path,source='fixture',max_sentences=1))),1)
            with self.assertRaises(ImportLimitError): list(iter_conllu(path,source='fixture',max_bytes=10))
