"""Held-out phrase bank: new programs, new wording for every restatement, history line, interval and as-of claim.
Committed to git before the first run and never edited after. The checker and DEFAULT_FACTS are unchanged."""

PROGRAMS = [("Cosmetics PFAS Disclosure Rule", "the Department of Toxic Substances"), ("Warehouse Quota Law", "the Workforce Agency"),
            ("Deforestation-Free Sourcing Regulation", "the Forestry Commission"), ("Data Broker Registration Rule", "the Privacy Protection Agency"),
            ("Scope 3 Disclosure Regulation", "the Securities Commission"), ("Right-to-Repair Parts Rule", "the Consumer Affairs Office"),
            ("Heat Illness Prevention Standard", "the Occupational Safety Board"), ("Plastic Bag Fee Ordinance", "the City Council")]
NUMWORD = {10: "ten", 14: "fourteen", 21: "twenty-one", 30: "thirty", 45: "forty-five", 60: "sixty", 3: "three", 2: "two"}

RESTATE = {
    "deadline": {
        "pill": ["Filing due {v}", "Next deadline: {v}", "Reports due by {v}"],
        "glance": ["Initial filing deadline | {v}", "When reports are due | {v}", "Compliance date | {v}"],
        "overview": ["In-scope businesses must submit their first report by {v}.", "The reporting deadline now stands at {v}.",
                     "Filers have until {v} to submit."],
        "body": ["{agency} expects the first filings on {v}.", "Reports under the {prog} are due on {v}, per the current notice.",
                 "The first annual report must be filed by {v}."],
        "faq": ["What date should we plan around? The first report is due {v}.", "How long do we have? You must report by {v}.",
                "Is there a filing deadline yet? Yes: {v}."],
        "timeline": ["{v} | Initial reports due", "{v} | Compliance date for the {prog}", "{v} | Deadline to submit first report"]},
    "comment_close": {
        "pill": ["Comment window closes {v}", "Comments accepted through {v}"],
        "glance": ["Public comment | open through {v}", "Comment deadline | {v}"],
        "overview": ["The public comment window closes {v}.", "Stakeholders have until {v} to comment."],
        "body": ["Comments on the draft are due {v}.", "{agency} will accept comments through {v}.",
                 "The consultation closes {v}."],
        "faq": ["Is it too late to comment? No, the comment period runs through {v}.", "How do we weigh in? File comments by {v}."],
        "timeline": ["{v} | Public comment window closes", "{v} | Last day for comments"]},
}
STAGE = {
    "proposed": {"pill": ["Draft rule · not yet final", "Still a proposal"], "glance": ["Rule status | still proposed", "Stage | awaiting final approval"],
                 "overview": ["The rule is still only a proposal.", "Nothing is final yet: the regulation is pending approval."],
                 "body": ["For now the regulation is proposed and not yet in effect.", "{agency} has not yet approved the rule, which remains proposed."],
                 "faq": ["Is the rule binding? Not yet: it remains a proposal.", "Has it been approved? No, it is still proposed."],
                 "timeline": ["TBD | Final approval of the rule", "Pending | Rule awaits final approval"]},
    "final": {"pill": ["Rule final", "In force"], "glance": ["Rule status | final and in effect", "Stage | now in force"],
              "overview": ["The rule is now in effect.", "The regulation has been approved and is final."],
              "body": ["{agency} approved the rule, which is now final.", "The regulation took effect and is now final."],
              "faq": ["Is the rule binding? Yes, it is now in effect.", "Has it been approved? Yes, it is final."],
              "timeline": ["Done | The rule is final", "Done | Rule approved; now in effect"]},
}
HISTORY = {
    "deadline": ["{agency} pushed the date back from {old} to {new}.", "Filers were initially looking at {old}.",
                 "The earlier {old} date was replaced by {new}."],
    "comment_close": ["The window was first set to close {old}.", "{agency} extended comments from {old} to {new}."],
    "stage": ["The rule was proposed and later approved.", "It was a proposal until approval."]}
HISTORY_IN_BODY = {
    "deadline": ["Before the extension, filers faced {old}.", "The {old} date no longer applies.", "The prior {old} target was dropped by {agency}.",
                 "Companies that planned for {old} gained extra time."],
    "comment_close": ["The original {old} close date was extended.", "Comments had been due {old}.", "Groups asked for more time past {old}."],
    "stage": ["Earlier drafts were proposals.", "The rule was only proposed in the spring."]}
CHANGELOG = {
    "deadline": ["{ev} — deadline updated: {old} → {new}.", "{ev} — the reporting date moved to {new} (from {old})."],
    "comment_close": ["{ev} — comment window now closes {new}; it was {old}.", "{ev} — comment deadline {old} → {new}."],
    "stage": ["{ev} — status {old} → {new}.", "{ev} — rule approved; was {old}."]}
MATH = ["The agency answered on {d2}, {n} {unit} after the request filed {d1}.",
        "Objections closed {d2}, {n} {unit} following the order of {d1}.",
        "The interim rule lapsed on {d2}, {n} {unit} from its start on {d1}.",
        "Its decision came {d2}, {n} {unit} after the hearing held {d1}."]
FUTURE = ["{agency} is set to hold a listening session on {d}.", "A stakeholder workshop is expected on {d}.",
          "The board will vote on {d}.", "An enforcement memo is due {d}."]
PAST = ["{agency} held a listening session on {d}.", "The stakeholder workshop took place on {d}.", "The board voted on {d}."]
ASOF = ["As of {d}, the regulator's website still shows the old guidance.", "As of {d}, the court docket shows no ruling.",
        "As of {d}, the state register has not published the notice."]
FILLER = ["The enabling statute dates from {d}.", "{agency} released an FAQ on {d}.", "A companion bill was filed {d}.",
          "The governor's office issued a statement on {d}."]
