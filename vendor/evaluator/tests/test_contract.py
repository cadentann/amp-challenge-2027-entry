import csv, hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scorer',ROOT/'score_batch.py')
scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)

class Contract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def prepare(self, rows, **changes):
        p=self.r/'input.csv'
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['candidate_id','sequence']);w.writeheader();w.writerows(rows)
        a={'parent_protocol_sha256':scorer.PARENT_SHA256,'parent_go':True,'purpose':'public_fixture',
           'input_path':str(p),'input_sha256':scorer.sha(p),'row_count':len(rows),'protected_reserve':False}
        a.update(changes);q=self.r/'auth.json';q.write_text(json.dumps(a));return p,q
    def test_exact_order_and_duplicate_sequence_mapping(self):
        p,q=self.prepare([{'candidate_id':'b','sequence':'ACDEFGHI'},{'candidate_id':'a','sequence':'ACDEFGHI'}])
        rows,seqs,_=scorer.load_input(p,q,'public_fixture')
        self.assertEqual([r['candidate_id'] for r in rows],['b','a']);self.assertEqual(seqs,['ACDEFGHI'])
    def test_duplicate_id_rejected(self):
        p,q=self.prepare([{'candidate_id':'a','sequence':'ACDEFGHI'}]*2)
        with self.assertRaises(AssertionError):scorer.load_input(p,q,'public_fixture')
    def test_invalid_sequence_not_repaired(self):
        for s in ['acdefghi','ACDEFGHX','ACDEFGH','A'*51,'ACDE FGHI']:
            p,q=self.prepare([{'candidate_id':'a','sequence':s}])
            with self.assertRaises(AssertionError):scorer.load_input(p,q,'public_fixture')
    def test_hash_change_rejected(self):
        p,q=self.prepare([{'candidate_id':'a','sequence':'ACDEFGHI'}]);p.write_text(p.read_text()+'\n')
        with self.assertRaises(AssertionError):scorer.load_input(p,q,'public_fixture')
    def test_no_parent_go_or_wrong_purpose(self):
        for changes in [{'parent_go':False},{'purpose':'qualified_pool'},{'protected_reserve':True}]:
            p,q=self.prepare([{'candidate_id':'a','sequence':'ACDEFGHI'}],**changes)
            with self.assertRaises(AssertionError):scorer.load_input(p,q,'public_fixture')
    def test_runtime_hashes_and_all_eleven_models(self):
        _,c=scorer.verify_runtime();self.assertEqual(len(c['apex_weights']),8);self.assertEqual(len(c['ania_weights']),3)

if __name__=='__main__':unittest.main()
