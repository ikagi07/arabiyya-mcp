# -*- coding: utf-8 -*-
"""البديع: ما لا يستحيل بالانعكاس (القلب)، ما يُقرأ من آخره حرفًا حرفًا كما يُقرأ من أوله."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sarf_mcp as M

KEY = "ما لا يستحيل بالانعكاس (القلب)"


def qalb(text):
    found = M.detect_badi(text)["المحسنات"]
    return found.get(KEY, []) if isinstance(found, dict) else []


class TestQalb(unittest.TestCase):
    def test_arrajani_whole_verse(self):
        # بيت الأرّجاني: 29 حرفًا، يُقرأ من آخره كما يُقرأ من أوله (نهاية الأرب ج7 ص171)
        p = qalb("مَوَدَّتُهُ تَدُومُ لِكُلِّ هَوْلٍ * وَهَلْ كُلٌّ مَوَدَّتُهُ تَدُومُ")
        self.assertEqual([(x["نطاقه"], x["عدد الحروف"]) for x in p], [("البيت كله", 29)])

    def test_hariri_phrases(self):
        # من الحريري (خريدة القصر ص662)، والهمزة على الألف ألفٌ في القلب
        for t in ("ساكب كاس", "لم أخامل", "كبّر رجاءَ أجرِ ربّك"):
            self.assertTrue(qalb(t), t)

    def test_quran_examples(self):
        self.assertTrue(qalb("كل في فلك"))
        p = qalb("وربك فكبر")       # من غير الواو
        self.assertEqual((p[0]["عدد الحروف"], "تنبيه" in p[0]), (7, True))

    def test_ordinary_verse_has_none(self):
        self.assertEqual(qalb("قفا نبك من ذكرى حبيب ومنزل * بسقط اللوى بين الدخول فحومل"), [])


def found(text, key):
    f = M.detect_badi(text)["المحسنات"]
    return f.get(key, []) if isinstance(f, dict) else []


def jinas(text):
    return {(tuple(x["اللفظان"]), x["نوعه"].split(" (")[0]) for x in found(text, "الجناس")}


class TestBadiRound2(unittest.TestCase):
    """شواهد الدورة الثانية (eval/gold/badi_round2_candidates.jsonl)."""

    def test_muharraf(self):
        # المهمة 09: بغية الإيضاح ج4 ص643
        self.assertIn((("البُرد", "البَرد"), "جناس محرّف"), jinas("جُبَّة البُرد جُنَّة البَرد"))
        self.assertIn((("الشِّعر", "الشَّعر"), "جناس محرّف"),
                      jinas("والحسن يظهر في بيتين رونقه * بيت من الشِّعر أو بيت من الشَّعر"))
        # بلا ضبط لا يُحكم بالتحريف
        self.assertNotIn("جناس محرّف", {k for _, k in jinas("بيت من الشعر أو بيت من الشعر")})


if __name__ == "__main__":
    unittest.main()
