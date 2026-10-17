"""Dev phrase bank (the checker was built against this one)."""

PROGRAMS = [("Packaging EPR Rule", "the Recycling Board"), ("Battery Labelling Regulation", "the Environment Agency"),
            ("Pay Transparency Act", "the Labor Department"), ("AI Hiring Audit Rule", "the Civil Rights Office"),
            ("Microplastics Reporting Rule", "the Water Board"), ("Supplier Due Diligence Law", "the Trade Ministry")]
NUMWORD = {10: "ten", 14: "fourteen", 21: "twenty-one", 30: "thirty", 45: "forty-five", 60: "sixty", 3: "three", 2: "two"}

RESTATE = {
    "deadline": {
        "pill": ["First deadline {v}", "Reports due {v}"],
        "glance": ["First report due | {v}", "Deadline | {v}"],
        "overview": ["The first deadline is {v}.", "Covered companies must file by {v}."],
        "body": ["Under the {prog}, the first report is due {v}.", "The filing deadline set by {agency} is {v}."],
        "faq": ["When is the first report due? Reports are due {v}.", "What is the deadline? The deadline is {v}."],
        "timeline": ["{v} | First reports due under the {prog}", "{v} | Filing deadline"]},
    "comment_close": {
        "pill": ["Comments close {v}", "Comment period open until {v}"],
        "glance": ["Comment period | closes {v}", "Comments due | {v}"],
        "overview": ["Comments are due {v}.", "The comment period closes {v}."],
        "body": ["{agency} is taking comments; the comment period closes {v}.", "Written comments are due {v}."],
        "faq": ["Can we still comment? Yes, comments are due {v}.", "When does the comment period close? On {v}."],
        "timeline": ["{v} | Comment period closes", "{v} | Comments due"]},
}
STAGE = {
    "proposed": {"pill": ["Rule proposed · not final", "Proposal stage"], "glance": ["Stage | The rule remains proposed", "Status | pending approval"],
                 "overview": ["The rule remains proposed.", "The regulation is still a proposal and awaits approval."],
                 "body": ["Until approval, the rule is proposed, not final.", "The regulation remains proposed while {agency} reviews it."],
                 "faq": ["Is the rule final? No, it is still proposed.", "Is it in force? Not yet final."],
                 "timeline": ["Pending | Final approval of the rule", "Next | Rule awaits approval"]},
    "final": {"pill": ["Rule final · in effect", "Rule in effect"], "glance": ["Stage | The rule is now final", "Status | in effect"],
              "overview": ["The rule is now final.", "The regulation is in effect."],
              "body": ["The rule is final and in effect.", "The regulation has been approved and is in effect."],
              "faq": ["Is the rule final? Yes, the rule is now final.", "Is it in force? Yes, it is in effect."],
              "timeline": ["Done | Rule approved and in effect", "Done | The rule is now final"]},
}
HISTORY = {
    "deadline": ["The deadline was moved from {old} to {new}.", "{agency} originally set the deadline at {old}."],
    "comment_close": ["Comments were due {old} before the extension to {new}.", "The comment period was originally set to close {old}."],
    "stage": ["The rule had been proposed before approval.", "Before approval, the regulation was proposed."]}
HISTORY_IN_BODY = {
    "deadline": ["The deadline had been {old} before {agency} moved it.", "Previously the first report was due {old}."],
    "comment_close": ["Comments were previously due {old}.", "The comment period was extended from {old}."],
    "stage": ["The rule was proposed earlier this year.", "Earlier, the regulation was only proposed."]}
CHANGELOG = {
    "deadline": ["{ev}: {agency} moved the deadline from {old} to {new}.", "{ev}: deadline changed from {old} to {new}."],
    "comment_close": ["{ev}: comment period extended from {old} to {new}.", "{ev}: comments now due {new} (was {old})."],
    "stage": ["{ev}: the rule moved from {old} to {new}.", "{ev}: approved; stage changed from {old} to {new}."]}
MATH = ["The hearing record closed {d2}, {n} {unit} after the hearing on {d1}.",
        "{agency} issued its response on {d2}, {n} {unit} after the petition of {d1}.",
        "The notice took effect {d2}, {n} {unit} after publication on {d1}."]
FUTURE = ["A public hearing is scheduled for {d}.", "{agency} will publish guidance on {d}.", "The next workshop is upcoming on {d}."]
PAST = ["A public hearing was held on {d}.", "{agency} published guidance on {d}.", "The last workshop took place on {d}."]
ASOF = ["As of {d}, the {agency} docket still shows no final decision.", "As of {d}, the agency page still lists the rule as under review."]
FILLER = ["The statute was enacted on {d}.", "{agency} posted a fact sheet dated {d}.", "A related bill was introduced on {d}."]
