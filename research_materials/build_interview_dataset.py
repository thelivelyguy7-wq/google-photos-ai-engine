"""Build the synthetic user-interview dataset.

SYNTHETIC: every participant below is an AI-written persona used to rehearse the interview guide,
the first-failing-node coding and the MVP test protocol. No person was interviewed. Tag every use
[SYN-INTERVIEW]; never merge with [OBS-PRIMARY] evidence.

n = 6 participants (a rehearsal round, not the full n = 16 in screener_and_consent.md):
  effortful path 3 · failed / gave up 1 · heavy library (30k+) 2. P03 also ran a quick-success contrast task.

Outputs (next to this file):
  synthetic_interviews.csv      one row per observed retrieval task (7 tasks, 6 participants)
  synthetic_mvp_test.csv        one row per participant in the MVP task test (6 participants)
  synthetic_interview_summary.md aggregates computed from the two CSVs

Run: python research_materials/build_interview_dataset.py
"""
import csv
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

# Node codes: D1 Recall · D2 Express · D3 Understand & match · D4 Evaluate · D5 Refine · D6 Available
# outcome: found_quick | found_effort | found_outside (found via another app/person) | not_found | not_in_library
# used_distinctive = did the FIRST query contain the participant's most distinctive remembered clue?
INTERVIEW_FIELDS = [
    "pid", "task_id", "age", "city", "occupation", "device", "library_items", "search_freq", "screener_group",
    "task", "object_type", "remembered", "distinctive_clue", "forgotten", "first_query", "used_distinctive",
    "queries", "strategies", "time_s", "outcome", "first_failing_node", "secondary_node",
    "H1_expression", "H2_recognition", "H3_time_scope", "H4_unguided_recovery", "workaround", "quote",
]

T = [
    # --- carried over from synthetic_interview_notes.md (SYN-P1..P6) ---
    dict(pid="P01", task_id="P01-T1", age=29, city="Bengaluru", occupation="Product designer", device="Android",
         library_items=22000, search_freq="monthly", screener_group="effortful",
         task="Small cafe from a Goa trip", object_type="photo",
         remembered="Goa trip; end of 2023; friend Rhea in frame; cold coffee; blue door",
         distinctive_clue="blue door", forgotten="cafe name; exact date; whose phone",
         first_query="cafe goa", used_distinctive="N", queries=2, strategies="search;scroll;open-each;other-app",
         time_s=540, outcome="found_outside", first_failing_node="D2", secondary_node="D4",
         H1_expression="supported", H2_recognition="supported", H3_time_scope="partial", H4_unguided_recovery="not observed",
         workaround="Searched WhatsApp chat with friend for a forwarded copy",
         quote="I type the thing I'd put on an album name, not the thing I actually remember."),
    dict(pid="P02", task_id="P02-T1", age=41, city="Pune", occupation="School teacher", device="iPhone",
         library_items=9000, search_freq="rarely", screener_group="failed",
         task="Medicine strip with dosage written in pen", object_type="photo",
         remembered="Fever, monsoon 2024; blister strip; dosage handwritten on box",
         distinctive_clue="pen writing on box", forgotten="brand name; month",
         first_query="medicine", used_distinctive="N", queries=2, strategies="search;scroll",
         time_s=330, outcome="not_in_library", first_failing_node="D6", secondary_node="",
         H1_expression="not observed", H2_recognition="not observed", H3_time_scope="not observed", H4_unguided_recovery="not observed",
         workaround="Taken in WhatsApp camera, never backed up; found in chat with spouse",
         quote="I assumed Google Photos has everything from my phone."),
    dict(pid="P03", task_id="P03-T2", age=34, city="Delhi", occupation="Chartered accountant", device="Android",
         library_items=35000, search_freq="weekly", screener_group="heavy_library",
         task="Workshop whiteboard with a funnel diagram", object_type="photo",
         remembered="Offsite workshop; red and green marker funnel; '2022, before I changed jobs'",
         distinctive_clue="funnel drawing", forgotten="words on board; month",
         first_query="whiteboard", used_distinctive="N", queries=3, strategies="search;date-scrub;scroll;other-app",
         time_s=360, outcome="found_outside", first_failing_node="D5", secondary_node="D3",
         H1_expression="partial", H2_recognition="not observed", H3_time_scope="supported", H4_unguided_recovery="supported",
         workaround="Messaged the colleague who ran the workshop; photo was from 2021",
         quote="When I set a year I'm basically betting on it. If I'm wrong, I don't know I'm wrong."),
    dict(pid="P03", task_id="P03-T1", age=34, city="Delhi", occupation="Chartered accountant", device="Android",
         library_items=35000, search_freq="weekly", screener_group="heavy_library",
         task="Page 2 of a rent agreement", object_type="document",
         remembered="Rent agreement; printed words", distinctive_clue="printed title text", forgotten="date",
         first_query="rent agreement", used_distinctive="Y", queries=1, strategies="search",
         time_s=20, outcome="found_quick", first_failing_node="none", secondary_node="",
         H1_expression="not observed", H2_recognition="not observed", H3_time_scope="not observed", H4_unguided_recovery="not observed",
         workaround="", quote="The words were on the page, so it just worked."),
    dict(pid="P04", task_id="P04-T1", age=52, city="Jaipur", occupation="Textile shop owner", device="Android",
         library_items=15000, search_freq="never", screener_group="effortful",
         task="Grandson's first birthday cake", object_type="photo",
         remembered="Blue car-shaped cake; at home; yellow shirt; winter ~2 years ago",
         distinctive_clue="car-shaped cake", forgotten="date; who took it",
         first_query="(none - scrolled)", used_distinctive="N", queries=0, strategies="scroll",
         time_s=360, outcome="found_effort", first_failing_node="D2", secondary_node="",
         H1_expression="supported", H2_recognition="not observed", H3_time_scope="not observed", H4_unguided_recovery="not observed",
         workaround="Scrolls the timeline or asks daughter",
         quote="Search is for when you know the name of the thing."),
    dict(pid="P05", task_id="P05-T1", age=24, city="Hyderabad", occupation="Postgraduate student", device="Android",
         library_items=48000, search_freq="daily", screener_group="heavy_library",
         task="Exam-season meme screenshot a friend sent", object_type="screenshot",
         remembered="Gist of joke; cartoon cat; black background; March",
         distinctive_clue="cartoon cat", forgotten="exact wording; sender; source app",
         first_query="syllabus meme", used_distinctive="N", queries=5, strategies="search;rephrase;scroll;other-app",
         time_s=600, outcome="found_outside", first_failing_node="D3", secondary_node="D5",
         H1_expression="weakened", H2_recognition="not observed", H3_time_scope="not observed", H4_unguided_recovery="supported",
         workaround="Asked friend group who sent it",
         quote="It just says nothing. Did it not find the cat or not find the words? No idea."),
    dict(pid="P06", task_id="P06-T1", age=37, city="Mumbai", occupation="Marketing manager", device="Android",
         library_items=27000, search_freq="weekly", screener_group="effortful",
         task="Beagle in a marigold garland at a Udaipur wedding", object_type="photo",
         remembered="Friend's wedding; Udaipur 2022; beagle; marigold garland; fairy lights",
         distinctive_clue="dog wearing marigold garland", forgotten="which wedding day; whose phone",
         first_query="dog wedding", used_distinctive="partial", queries=2, strategies="search;people-group;scroll",
         time_s=420, outcome="found_effort", first_failing_node="D5", secondary_node="",
         H1_expression="partial", H2_recognition="weakened", H3_time_scope="not observed", H4_unguided_recovery="supported",
         workaround="Pivoted to the friend's face group, then scrolled",
         quote="I knew three things about it. The app let me use one at a time."),
]

# MVP test: seeded library of 120 captioned items, one task per participant rebuilt from their own incident.
# Counterbalanced: half did baseline (keyword search + timeline) first. Success = correct item within 180 s,
# or (P02 only, target deliberately absent) a correct "not in library" conclusion within 180 s.
# SEQ = single ease question, 1 (very hard) to 7 (very easy).
MVP_FIELDS = ["pid", "seeded_task", "first_node_in_interview", "order",
              "baseline_success", "baseline_time_s", "baseline_queries", "baseline_seq",
              "mvp_success", "mvp_time_s", "mvp_turns", "mvp_seq",
              "clue_prompt_added_clue", "used_match_chips", "relaxed_a_clue", "note"]
M = [
    ("P01", "Cafe with a blue door, Goa", "D2", "B-M", "N", 180, 4, 3, "Y", 52, 2, 6, "Y", "Y", "N", "Clue prompt surfaced 'blue door'; target in top 3"),
    ("P02", "Medicine strip (deliberately absent from seed)", "D6", "M-B", "N", 180, 3, 2, "Y", 58, 2, 5, "N", "Y", "N", "No item matched all clues; MVP said it may not be backed up. Counts as correct"),
    ("P03", "Funnel whiteboard, wrong year given", "D5", "B-M", "N", 180, 3, 2, "Y", 71, 3, 6, "N", "Y", "Y", "Chip showed the year missed; relaxed to +/-1 year, found 2021"),
    ("P04", "Car-shaped birthday cake", "D2", "M-B", "Y", 164, 1, 3, "Y", 38, 2, 7, "Y", "N", "N", "Typed a full sentence: 'that is how I talk'"),
    ("P05", "Cat meme, paraphrased wording", "D3", "B-M", "N", 180, 5, 2, "Y", 88, 3, 5, "N", "Y", "Y", "Chips: cat matched, words missed; dropped the wording clue"),
    ("P06", "Beagle in a marigold garland", "D5", "M-B", "Y", 151, 3, 4, "Y", 41, 1, 7, "N", "Y", "N", "Combined three clues in one message"),
]


def main():
    with open(HERE / "synthetic_interviews.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INTERVIEW_FIELDS)
        w.writeheader()
        for row in T:
            w.writerow(row)
    with open(HERE / "synthetic_mvp_test.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(MVP_FIELDS)
        w.writerows(M)
    (HERE / "synthetic_interview_summary.md").write_text(summary(), encoding="utf-8")
    write_xlsx(HERE / "synthetic_interview_dataset.xlsx")
    print("wrote synthetic_interviews.csv, synthetic_mvp_test.csv, synthetic_interview_summary.md, "
          "synthetic_interview_dataset.xlsx")


FIELD_GUIDE = {
    "pid": "Participant ID (synthetic persona)",
    "task_id": "Task ID. P03-T1 is the quick-success contrast task; every other row is the participant's recalled incident",
    "age": "Age in years", "city": "City (India)", "occupation": "Occupation", "device": "Phone platform",
    "library_items": "Approximate photos and videos in the Google Photos library",
    "search_freq": "Self-reported search frequency",
    "screener_group": "Screener quota group: effortful, failed, heavy_library",
    "task": "The photo the participant was trying to find",
    "object_type": "photo, screenshot, document or video",
    "remembered": "What they remembered at the start",
    "distinctive_clue": "Their most distinctive remembered clue",
    "forgotten": "What they could not recall",
    "first_query": "Exact first query typed (or 'none' if they scrolled)",
    "used_distinctive": "Did the first query contain the distinctive clue? Y / N / partial",
    "queries": "Number of queries typed", "strategies": "Strategies used, in order (semicolon-separated)",
    "time_s": "Time to resolution in seconds",
    "outcome": "found_quick, found_effort, found_outside (via another app or person), not_in_library",
    "first_failing_node": "First retrieval step that failed: D1 Recall, D2 Express, D3 Understand & match, "
                          "D4 Evaluate, D5 Refine, D6 Available; 'none' if it succeeded",
    "secondary_node": "A second step that also failed, if any",
    "H1_expression": "H1 memory richer than expressed", "H2_recognition": "H2 target present but not recognised",
    "H3_time_scope": "H3 date used because easy, not reliable", "H4_unguided_recovery": "H4 no signal on why a query missed",
    "workaround": "What they did instead", "quote": "Verbatim quote (synthetic)",
    "seeded_task": "MVP test: the participant's incident rebuilt in a seeded test library",
    "first_node_in_interview": "First failing node from the interview",
    "order": "B-M = baseline first, then MVP; M-B = MVP first",
    "baseline_success": "Found with keyword search + timeline within 180 s (Y/N)",
    "baseline_time_s": "Baseline time, seconds (capped at 180)", "baseline_queries": "Baseline queries typed",
    "baseline_seq": "Baseline ease, Single Ease Question 1 (very hard) to 7 (very easy)",
    "mvp_success": "Found with the clue-guided MVP within 180 s (Y/N). P02: target deliberately absent; "
                   "Y = MVP correctly said it may not be in the library",
    "mvp_time_s": "MVP time, seconds (capped at 180)", "mvp_turns": "MVP conversation turns",
    "mvp_seq": "MVP ease, SEQ 1 to 7",
    "clue_prompt_added_clue": "The MVP's follow-up question drew out a clue the participant had not typed (Y/N)",
    "used_match_chips": "Used the matched / missed clue chips (Y/N)", "relaxed_a_clue": "Used one-tap clue relaxing (Y/N)",
    "note": "Observer note",
}


def write_xlsx(path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter as col
    from openpyxl.worksheet.formula import ArrayFormula

    F = "Arial"
    head_font = Font(name=F, bold=True, color="FFFFFF")
    head_fill = PatternFill("solid", fgColor="0B5CAD")
    body = Font(name=F)
    bold = Font(name=F, bold=True)
    thin = Border(bottom=Side(style="thin", color="D5DCE5"))
    wrap = Alignment(wrap_text=True, vertical="top")

    def table(ws, headers, rows, widths):
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = head_font, head_fill, Alignment(wrap_text=True, vertical="center")
        for r in rows:
            ws.append(list(r))
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment, c.border = body, wrap, thin
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[col(i)].width = w
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = ws.dimensions

    wb = Workbook()
    rd = wb.active
    rd.title = "README"
    lines = [
        ("Synthetic user interview dataset: Google Photos retrieval", True),
        ("SYNTHETIC. NOT REAL PARTICIPANTS. Every participant is an AI-written persona used to rehearse the interview "
         "guide, the first-failing-node coding and the MVP test protocol. No person was interviewed.", True),
        ("", False),
        ("Research question: how do people retrieve a photo they remember but cannot precisely describe, "
         "and where does that break down?", False),
        ("Method: 30-minute remote sessions on the participant's own phone. Part A: recall a recent retrieval incident. "
         "Part B: retry it live while thinking aloud. Each task is coded by the first retrieval step that failed.", False),
        ("Sample: 6 participants (effortful path 3, failed 1, heavy library 30k+ items 2); 7 observed tasks.", False),
        ("MVP test: the same 6 participants; own incident rebuilt in a seeded library; keyword search + timeline "
         "vs clue-guided MVP, order counterbalanced; success = right photo within 180 s.", False),
        ("", False),
        ("Sheets: Interviews (one row per task) · MVP_Test (one row per participant) · Summary (live formulas "
         "over both sheets) · Field_Guide (every column explained).", False),
        ("Source: generated by research_materials/build_interview_dataset.py; the CSV files hold the same data.", False),
    ]
    for text, b in lines:
        rd.append([text])
        rd.cell(rd.max_row, 1).font = Font(name=F, bold=b, size=14 if rd.max_row == 1 else 11,
                                           color="B45309" if rd.max_row == 2 else "1B1F24")
        rd.cell(rd.max_row, 1).alignment = Alignment(wrap_text=True, vertical="top")
    rd.column_dimensions["A"].width = 120

    iv = wb.create_sheet("Interviews")
    widths = {"task": 30, "remembered": 44, "distinctive_clue": 24, "forgotten": 26, "first_query": 20,
              "strategies": 28, "workaround": 40, "quote": 50, "occupation": 20, "outcome": 15}
    table(iv, INTERVIEW_FIELDS, ([t[f] for f in INTERVIEW_FIELDS] for t in T),
          [widths.get(f, 13) for f in INTERVIEW_FIELDS])

    mv = wb.create_sheet("MVP_Test")
    mw = {"seeded_task": 36, "note": 50}
    table(mv, MVP_FIELDS, M, [mw.get(f, 13) for f in MVP_FIELDS])

    # ---- Summary: every number is a formula over the two data sheets ----
    n = len(T) + 1
    rng = lambda f: f"Interviews!${col(INTERVIEW_FIELDS.index(f) + 1)}$2:${col(INTERVIEW_FIELDS.index(f) + 1)}${n}"
    node, outc, used, secs, pid = (rng(f) for f in ("first_failing_node", "outcome", "used_distinctive", "time_s", "pid"))
    mr = len(M) + 1
    mc = lambda f: f"MVP_Test!${col(MVP_FIELDS.index(f) + 1)}$2:${col(MVP_FIELDS.index(f) + 1)}${mr}"

    sm = wb.create_sheet("Summary")
    sm.column_dimensions["A"].width = 58
    sm.column_dimensions["B"].width = 16
    sm.column_dimensions["C"].width = 16
    rows = []

    def section(title, c2="", c3=""):
        rows.append(("H", title, c2, c3))

    def line(label, f2, f3=None):
        rows.append(("R", label, f2, f3))

    section("Sample", "Value")
    line("Participants", f"=SUMPRODUCT(1/COUNTIF({pid},{pid}))")
    line("Observed tasks", f"=COUNTA({pid})")
    line("Effortful or failed incidents", f'=COUNTIF({node},"<>none")')
    line("First query omitted or only partly used the distinctive clue",
         f'=COUNTIFS({used},"<>Y",{node},"<>none")')
    line("Median time, effortful or failed (s)", ("ARRAY", f'=MEDIAN(IF({node}<>"none",{secs}))'))
    line("Median time, quick success (s)", ("ARRAY", f'=MEDIAN(IF({outc}="found_quick",{secs}))'))
    section("First failing node", "Incidents")
    for k, name in (("D1", "D1 Recall"), ("D2", "D2 Express"), ("D3", "D3 Understand & match"),
                    ("D4", "D4 Evaluate"), ("D5", "D5 Refine"), ("D6", "D6 Available")):
        line(name, f'=COUNTIF({node},"{k}")')
    section("Outcome", "Tasks")
    for o in ("found_quick", "found_effort", "found_outside", "not_in_library"):
        line(o, f'=COUNTIF({outc},"{o}")')
    section("MVP task test", "Baseline", "MVP")
    line("Found within 180 s", f'=COUNTIF({mc("baseline_success")},"Y")', f'=COUNTIF({mc("mvp_success")},"Y")')
    line("Median time (s, capped at 180)", f'=MEDIAN({mc("baseline_time_s")})', f'=MEDIAN({mc("mvp_time_s")})')
    line("Median queries (baseline) / turns (MVP)", f'=MEDIAN({mc("baseline_queries")})', f'=MEDIAN({mc("mvp_turns")})')
    line("Mean ease, SEQ 1 to 7", f'=AVERAGE({mc("baseline_seq")})', f'=AVERAGE({mc("mvp_seq")})')
    line("Clue prompt drew out an untyped clue", None, f'=COUNTIF({mc("clue_prompt_added_clue")},"Y")')
    line("Used matched / missed chips", None, f'=COUNTIF({mc("used_match_chips")},"Y")')
    line("Relaxed a clue", None, f'=COUNTIF({mc("relaxed_a_clue")},"Y")')

    for i, (kind, a, b, c) in enumerate(rows, 1):
        if kind == "H":
            for j, v in enumerate((a, b, c), 1):
                cell = sm.cell(i, j, v or None)
                cell.font, cell.fill = head_font, head_fill
            continue
        sm.cell(i, 1, a).font = body
        for j, v in ((2, b), (3, c)):
            if v is None:
                continue
            ref = f"{col(j)}{i}"
            if isinstance(v, tuple):
                sm[ref] = ArrayFormula(ref, v[1])
            else:
                sm[ref] = v
            sm[ref].font = bold
            sm[ref].number_format = "0.0" if "AVERAGE" in str(v) else "0"
    sm.cell(len(rows) + 2, 1, "All values are live formulas over the Interviews and MVP_Test sheets.").font = \
        Font(name=F, italic=True, color="4A5361")

    fg = wb.create_sheet("Field_Guide")
    guide = [(f, "Interviews", FIELD_GUIDE[f]) for f in INTERVIEW_FIELDS] + \
            [(f, "MVP_Test", FIELD_GUIDE[f]) for f in MVP_FIELDS if f != "pid"]
    table(fg, ["column", "sheet", "meaning"], guide, [26, 14, 100])
    fg.freeze_panes = "A2"

    wb.calculation.fullCalcOnLoad = True
    wb.save(path)


def stats():
    """All headline numbers used by the summary and the deck."""
    main_tasks = [t for t in T if t["task_id"] != "P03-T1"]  # one recalled incident per participant
    hard = [t for t in main_tasks if t["first_failing_node"] != "none"]
    nodes = Counter(t["first_failing_node"] for t in hard)
    outcomes = Counter(t["outcome"] for t in main_tasks)
    withheld = [t for t in hard if t["used_distinctive"] != "Y"]
    b_ok = sum(r[4] == "Y" for r in M)
    m_ok = sum(r[8] == "Y" for r in M)
    return dict(
        n_participants=len({t["pid"] for t in T}), n_tasks=len(T), n_main=len(main_tasks), n_hard=len(hard),
        nodes=nodes, outcomes=outcomes, n_withheld=len(withheld),
        n_left_product=sum(t["outcome"] in ("found_outside",) or "other-app" in t["strategies"] for t in hard),
        median_time_hard=statistics.median(t["time_s"] for t in hard),
        median_time_quick=statistics.median(t["time_s"] for t in T if t["outcome"] == "found_quick"),
        groups=Counter(t["screener_group"] for t in main_tasks),
        h={h: Counter(t[h] for t in main_tasks) for h in ("H1_expression", "H2_recognition", "H3_time_scope", "H4_unguided_recovery")},
        mvp_n=len(M), b_ok=b_ok, m_ok=m_ok,
        b_time=statistics.median(r[5] for r in M), m_time=statistics.median(r[9] for r in M),
        b_q=statistics.median(r[6] for r in M), m_turns=statistics.median(r[10] for r in M),
        b_seq=statistics.mean(r[7] for r in M), m_seq=statistics.mean(r[11] for r in M),
        n_prompt_added=sum(r[12] == "Y" for r in M), n_chips=sum(r[13] == "Y" for r in M),
        n_relaxed=sum(r[14] == "Y" for r in M),
        mvp_fail=[r[0] for r in M if r[8] != "Y"],
    )


def summary():
    s = stats()
    L = ["# Synthetic interview dataset — summary", "",
         "> **SYNTHETIC — NOT REAL PARTICIPANTS.** AI-written personas used to rehearse the method. Tag `[SYN-INTERVIEW]`.",
         "> Generated by `build_interview_dataset.py`; do not hand-edit.", "",
         f"- Participants: **{s['n_participants']}** (screener groups: " +
         ", ".join(f"{k} {v}" for k, v in s['groups'].items()) + ")",
         f"- Observed retrieval tasks: **{s['n_tasks']}** ({s['n_main']} recalled incidents + 1 quick-success contrast task)",
         f"- Effortful or failed incidents: **{s['n_hard']} of {s['n_main']}**",
         f"- First query omitted the most distinctive remembered clue: **{s['n_withheld']} of {s['n_hard']}**",
         f"- Median time, effortful/failed: **{s['median_time_hard']:.0f} s**; quick successes: **{s['median_time_quick']:.0f} s**",
         "", "## First failing node (effortful/failed incidents)", "", "| Node | Incidents |", "|---|---|"]
    names = {"D2": "D2 Express", "D5": "D5 Refine", "D3": "D3 Understand & match", "D4": "D4 Evaluate",
             "D6": "D6 Available", "D1": "D1 Recall"}
    for k in ("D2", "D5", "D3", "D4", "D6", "D1"):
        L.append(f"| {names[k]} | {s['nodes'].get(k, 0)} |")
    L += ["", "## Outcomes", "", "| Outcome | Incidents |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in s["outcomes"].most_common()]
    L += ["", "## Hypothesis verdicts (count of participants)", ""]
    for h, c in s["h"].items():
        L.append(f"- **{h}**: " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
    L += ["", f"## MVP task test (n = {s['mvp_n']}, seeded library, counterbalanced)", "",
          "| Measure | Baseline (keyword + timeline) | MVP (clue-guided) |", "|---|---|---|",
          f"| Found within 180 s | {s['b_ok']} of {s['mvp_n']} | {s['m_ok']} of {s['mvp_n']} |",
          f"| Median time (s, capped at 180) | {s['b_time']:.0f} | {s['m_time']:.0f} |",
          f"| Median queries / turns | {s['b_q']:.0f} | {s['m_turns']:.0f} |",
          f"| Mean ease (SEQ 1–7) | {s['b_seq']:.1f} | {s['m_seq']:.1f} |", "",
          f"- Clue prompt added a clue the participant had not typed: {s['n_prompt_added']} of {s['mvp_n']}",
          f"- Used match/miss chips: {s['n_chips']} of {s['mvp_n']}; relaxed a clue: {s['n_relaxed']} of {s['mvp_n']}",
          f"- MVP failures: {', '.join(s['mvp_fail']) or 'none'}. Untested failure modes: handwriting, near-identical videos (no participant hit them)", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
