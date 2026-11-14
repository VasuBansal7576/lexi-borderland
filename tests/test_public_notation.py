"""Notation clarification changes only the fixed room-1 language, never sampled facts."""
import copy,json,unittest
from pathlib import Path
from baseline.paid.run import PaidHistory
from baseline.interface_v3 import LAWS
from borderland.env import BorderlandEnv

ROOT=Path(__file__).resolve().parents[1]

class PublicNotationTests(unittest.TestCase):
    def test_prior_request_changes_only_by_generic_notation(self):
        old=json.loads((ROOT/'artifacts/codex-terra-episode-v1/live/call-01/public-messages.json').read_text())
        world=json.loads((ROOT/'artifacts/codex-terra-episode-v1/live/manifest.json').read_text())
        env=BorderlandEnv(world=world);history=PaidHistory()
        history.add({'ok':True,'result':{},'observation':env.observe()})
        current=history.messages();self.assertEqual(old[0],current[0])
        before=json.loads(old[1]['content']);after=json.loads(current[1]['content'])
        first='Room 1: glyphs A,B,C,D map bijectively to sectors 0..3.'
        extra=" Let K[g] denote the sector of glyph g. In a glyph_constraints record, each differences entry [a,b,d] means (K[a]-K[b]) mod 4 = d: subtract the second glyph's sector from the first. The phase_anchor entry [g,o] means (K[g]-phase) mod 4 = o. All mod 4 results are in 0..3."
        self.assertEqual(after['fixed_public_laws_for_this_room'],before['fixed_public_laws_for_this_room'].replace(first,first+extra))
        after['fixed_public_laws_for_this_room']=before['fixed_public_laws_for_this_room']
        self.assertEqual(after,before)  # evidence, actions, tool schemas and state are untouched

    def test_notation_is_identical_across_worlds_and_absent_after_wipe(self):
        fixed=[]
        for source in sorted((ROOT/'artifacts/certification-v1').glob('family-*/phase-*/manifest.json')):
            env=BorderlandEnv(world=json.loads(source.read_text()));history=PaidHistory()
            history.add({'ok':True,'result':{},'observation':env.observe()})
            fixed.append(json.loads(history.messages()[1]['content'])['fixed_public_laws_for_this_room'])
        self.assertEqual(len(fixed),64);self.assertEqual(len(set(fixed)),1)
        for room in range(2,8):self.assertNotIn('phase_anchor',LAWS[room])
        # Reconstruct an already saved, real post-wipe public frame offline.
        proof=ROOT/'artifacts/paid-adapter-offline/proof'
        report=next(json.loads(p.read_text()) for p in proof.glob('*/report.json') if json.loads(p.read_text())['wipes'])
        frame=copy.deepcopy(report['wipes'][0]['fresh_frame']);history=PaidHistory();history.add(frame)
        user=json.loads(history.messages()[1]['content'])
        self.assertEqual(len(user['history_since_last_wipe']['events']),1)
        self.assertEqual(user['current_state']['notebook'],frame['observation']['notebook'])
        self.assertNotIn('differences entry',user['fixed_public_laws_for_this_room'])

if __name__=='__main__':unittest.main()
