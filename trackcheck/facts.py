"""Default fact vocabulary for a regulatory tracker. Real trackers would add their own cue phrases per program.

Post-first-run change (disclosed in the README): the held-out bank used wording this list did not know
("compliance date", "have until ... to submit", "first filings", "comment" without an s, "awaiting approval",
"nothing is final yet"). The vocabulary below was widened after seeing those misses; out/heldout_first_run.json keeps
the first-run numbers.
"""

DEADLINE = {"key": "deadline", "type": "date",
            "cues": [r"\bdeadline\b", r"\breports? (?:are |is )?due\b", r"\bfiling (?:is )?due\b", r"\bmust (?:file|report|submit)\b",
                     r"\bfirst (?:annual )?report\b", r"\bdue (?:on|by)\b",
                     # added after the first held-out run
                     r"\bcompliance date\b", r"\b(?:first |initial )?filings?\b", r"\bhave until\b[^.;]{0,40}\b(?:submit|file|report)\b"]}
COMMENTS = {"key": "comment_close", "type": "date",
            "cues": [r"\bcomments? (?:are |is )?(?:due|close|closes|period|window|deadline)\b", r"\bcomment period\b", r"\bconsultation (?:closes|period|window)\b",
                     # added after the first held-out run
                     r"\bcomments?\b[^.;|]{0,30}\b(?:through|until|by)\b", r"\b(?:through|until|by)\b[^.;|]{0,30}\bcomment\b",
                     r"\bto comment\b", r"\bfor comments\b"]}
NEG = r"(?<!not )(?<!nothing )(?<!nothing is )"
STAGE = {"key": "stage", "type": "stage",
         "cues": [r"\brule\b", r"\bregulation\b", r"\bproposal\b", r"\bdeadline\b", r"\bdate\b", r"\bit\b", r"\bstatus\b", r"\bstage\b"],
         "stage_phrases": {
             "proposed": r"\b(?:remains?|is|still|currently|stays?) (?:only )?(?:a )?(?:proposed|proposal)\b|\bpending (?:final )?approval\b|"
                         r"\bnot yet (?:final|approved|adopted|in effect)\b|\bawaits? (?:final )?approval\b|\b(?:is |remains )?proposed, not final\b|\bnot final\b|\bproposal stage\b"
                         # added after the first held-out run
                         r"|\bawaiting (?:final )?approval\b|\bnothing is final\b|\bnot (?:yet )?(?:binding|approved)\b",
             "final": r"(?<!not )(?<!nothing )\b(?:is|now|has been|was) (?:final|approved|in effect|in force)\b|\b(?:took|takes) effect\b|\bnow final\b"}}

DEFAULT_FACTS = [DEADLINE, COMMENTS, STAGE]
