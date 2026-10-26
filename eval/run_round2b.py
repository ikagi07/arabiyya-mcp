#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""الدورة 2ب (تعديل الطلب #15 بمراجعة بليغ): قياس detect_badi على الدورة 1 (eval/gold/badi.jsonl) والدورة 2
(eval/gold/badi_round2_candidates.jsonl) والجمل العادية العشر وحالات بليغ (/workspace/review15/spot)، كله «داخل العينة».
التشغيل: python eval/run_round2b.py <tag>   (tag: base | after)
المخرجات: eval/reports/badi_round2b_<tag>.{json,md} ونسخ تقارير الدورتين باسم *_round2b_<tag>*"""
import sys, json, shutil, tempfile, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "gold_irab")); sys.path.insert(0, str(HERE.parent))
import run_gold as R
import run_round2 as R2
import sarf_mcp as S

TAG = sys.argv[1]
OUT = HERE / "reports"
SPOT = Path("/workspace/review15/spot")
GOLD_IN_TOOL = {frozenset(p) for p in [("حياة", "موت"), ("حي", "ميت"), ("احيا", "امات"), ("يحيي", "يميت"), ("حق", "باطل"),
               ("كثير", "قليل"), ("كثره", "قله"), ("اقبل", "ادبر"), ("اقبال", "ادبار"), ("حلو", "مر"), ("ضحك", "بكى"),
               ("ضحك", "بكاء"), ("بكاء", "ضحك"), ("يبكي", "يضحك"), ("جود", "بخل"), ("بخيل", "جواد")]}
ORIG_ANT, ORIG_GEN = list(S._ANTONYMS), S._general_antonyms
rev = subprocess.run(["git", "-C", str(HERE.parent), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()


def set_nogold(on):
    """on: False | "tsv" (حذف صفوف in_gold=yes من الملف العام وحده، وهو الرقم المعتمد) | "all" (ومعها أزواج الذهبي في _ANTONYMS)"""
    S._ANTONYMS[:] = [p for p in ORIG_ANT if not (on == "all" and frozenset(p) in GOLD_IN_TOOL)]
    if on:
        import csv
        tsv = HERE.parent / "data" / "badi" / "antonyms_general.tsv"
        bad = {frozenset((r["word1"], r["word2"])) for r in csv.DictReader(open(tsv, encoding="utf-8"), delimiter="\t") if r["in_gold"] == "yes"}
        S._general_antonyms = lambda t=None: [p for p in ORIG_GEN(t) if frozenset(p) not in bad]
    else:
        S._general_antonyms = ORIG_GEN
    S._antonym_index.cache_clear()


def r2_scores(rows, labels):
    el = [r for r in rows if not r["excluded"]]
    res = {}
    for nm, rs in (("with022", el), ("without022", [r for r in el if r["id"] != "badi2-022"])):
        s0, s1 = R2.bscore(rs, labels, False), R2.bscore(rs, labels, True)
        rs2 = json.loads(json.dumps(rs, ensure_ascii=False))
        for r in rs2:  # 007: التصريع صواب ثانوي (reclassified_after_run)
            for d in r["detections"]:
                if r["id"] == "badi2-007" and d["label"] == "التصريع":
                    d["secondary"] = True
        s2 = R2.bscore(rs2, labels, True)
        res[nm] = {"recall": s0["rec"], "prec_strict": s0["prec"], "prec_secondary_excluded": s1["prec"], "prec_secondary_excluded_007": s2["prec"],
                   "prec_with_out_of_gold_labels": s0["strict"], "neg_clean": s0["neg_clean"],
                   "hits": sorted(r["id"][-3:] for r in rs if r["hit"])}
    return res


def run_r2(nogold):
    set_nogold(nogold)
    tmp = Path(tempfile.mkdtemp()); R2.OUT = tmp
    rows, labels = R2.run_badi()
    if not nogold:
        for ext in ("md", "jsonl"):
            shutil.copy(tmp / f"badi_round2.{ext}", OUT / f"badi_round2b_{TAG}_round2.{ext}")
    return r2_scores(rows, labels), rows


def run_r1():
    set_nogold(False)
    tmp = Path(tempfile.mkdtemp()); R.OUT = tmp
    out = R.run_badi(); R.write_badi(*out)
    for ext in ("md", "jsonl"):
        shutil.copy(tmp / f"badi_pilot.{ext}", OUT / f"badi_round2b_{TAG}_round1.{ext}")
    rows = [json.loads(l) for l in (tmp / "badi_pilot.jsonl").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    book = [r for r in rows if r.get("variant") == "book"]
    labels = sorted({r["label"] for r in book if not r["negative"]})
    res = {}
    for nm, rs in (("A_all20", book), ("B_no_muhtamal", [r for r in book if r["status"] != "muhtamal"])):
        sc = R.badi_score(rs, labels)
        res[nm] = {"recall": sc["rec"], "prec": sc["prec"], "strict": sc["strict"], "neg_clean": sc["neg_clean"]}
    return res


def flat(r):
    out = []
    if isinstance(r, dict):
        for k, v in r.items():
            for x in v:
                if k in ("الجناس", "الطباق"):
                    out.append(f"{x.get('نوعه','').split(' (')[0]}: {'/'.join(x['اللفظان'])}")
                elif k == "المقابلة":
                    out.append(f"المقابلة: {x.get('الأزواج')}")
                elif k == "التصريع":
                    out.append(f"التصريع: {x['آخر الصدر']}/{x['آخر العجز']}")
                elif k == "السجع":
                    out.append(f"السجع: {'/'.join(x.get('الفاصلتان', []))}")
                else:
                    out.append(k)
    return out


def run_spot():
    set_nogold(False)
    cases = json.load(open(SPOT / "cases.json", encoding="utf-8")) + json.load(open(SPOT / "cases2.json", encoding="utf-8"))
    return {n: flat(S.detect_badi(t)["المحسنات"]) for n, t in cases}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    r2, _ = run_r2(False)
    r2ng, _ = run_r2("tsv")
    r2ng_all, _ = run_r2("all")
    r1 = run_r1()
    spot = run_spot()
    ordinary = {k: v for k, v in spot.items() if k.split()[0] in {f"P{i}" for i in range(1, 11)}}
    summ = {"_meta": {"tag": TAG, "commit": rev, "run_at": R.now(), "label": "داخل العينة", "antonym_tiers": S.ANTONYM_TIERS},
            "round2": r2, "round2_no_gold_pairs_tsv": r2ng, "round2_no_gold_pairs_all": r2ng_all, "round1": r1,
            "ordinary10": {"with_any_detection": sum(bool(v) for v in ordinary.values()), "n": len(ordinary), "detail": ordinary},
            "spot": spot}
    (OUT / f"badi_round2b_{TAG}.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k != "spot"}, ensure_ascii=False, indent=1))
