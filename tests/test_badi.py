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

    def test_pronoun_not_extra_letter(self):
        # المهمة 11: تحرير التحبير ص255، «قبله/قبل» ترديد لا جناس
        self.assertEqual([k for k in jinas("قل لمن ساد ثم ساد أبوه * قبله ثم قبل ذلك جده") if "قبله" in k[0]], [])

    def test_ha_wasl_vs_rawi(self):
        # المهمة 12: تحرير التحبير ص255، «أبوه» رويّها الهاء و«جده» رويّها الدال، فلا تصريع
        self.assertEqual(found("قل لمن ساد ثم ساد أبوه * قبله ثم قبل ذلك جده", "التصريع"), [])

    def test_root_ha_blocks_wasl_in_other_hemistich(self):
        # مراجعة #15 (بليغ وسقط الزند): «وجه» هاؤها أصلية، فلا تُجعل هاء «شبه» وصلًا وإن قرأها المحلّل «شَبَّهُ»
        self.assertTrue(found("له في الحسن وجه * وما للبدر شبه", "التصريع"))
        # وهاء الضمير بعد متحرك وصلٌ في الشطرين: الروي الدال في «جده/حده» والباء في «ربه/قلبه»
        self.assertTrue(found("أتى الفتى من جده * فأمضى السيف من حده", "التصريع"))

    def test_arud_gold_019_unchanged(self):
        # ذهبي العروض arud-019 (المعري، سقط الزند): الروي دال والهاء بعده وصل؛ ولا تصريع فيه («لا/وترفدها») كما كان
        for t in ("تُثْنِي عَلَيْكَ البِلَادُ أَنَّكَ لَا * تَأْخُذُ مِنْ رِفْدِهَا وَتَرْفِدُهَا",
                  "تثني عليك البلاد أنك لا * تأخذ من رفدها وترفدها"):
            self.assertEqual(found(t, "التصريع"), [])
        q = M.analyze_qafiya("تُثْنِي عَلَيْكَ البِلَادُ أَنَّكَ لَا * تَأْخُذُ مِنْ رِفْدِهَا وَتَرْفِدُهَا")
        self.assertEqual((q["الحكم العام"]["الروي"], q["الأبيات"][0]["الوصل"]), ("د", "ه"))

    def test_wa_la_negation(self):
        # المهمة 13: بغية الإيضاح ج4 ص576، «ونُنكر/ولا ينكرون» طباق سلب
        t = found("ونُنكر إن شئنا على الناس قولهم * ولا ينكرون القول حين نقول", "الطباق")
        self.assertIn((("ونُنكر", "ينكرون"), "طباق سلب (إثبات ونفي)"), {(tuple(x["اللفظان"]), x["نوعه"]) for x in t})

    def test_salb_same_verb(self):
        # مراجعة #15: طباق السلب فعل واحد مثبت ومنفي أو مأمور به ومنهي عنه؛ «تجبه/إجابته» فعل ومصدر فليس طباقًا
        self.assertEqual(found("إذا نطق السفيه فلا تجبه * وخير من إجابته السكوت", "الطباق"), [])
        t = found("فلا تخشوهم واخشون", "الطباق")
        self.assertIn((("تخشوهم", "واخشون"), "طباق سلب (إثبات ونفي)"), {(tuple(x["اللفظان"]), x["نوعه"]) for x in t})

    def test_comma_does_not_split_prose(self):
        # المهمة 15: بغية الإيضاح ج4 ص645 وص582
        t = "بيني وبين كِنِّي ليل دامس، وطريق طامس"
        self.assertIn((("دامس", "طامس"), "جناس مضارع"), jinas(t))
        self.assertTrue(found(t, "السجع"))      # والسجع باقٍ على الفاصلتين
        tb = found("ما أجمد في حق، ولا أذوب في باطل", "الطباق")
        self.assertIn(("حق", "باطل"), {tuple(x["اللفظان"]) for x in tb})

    def test_prose_window_one_sentence_and_next(self):
        # مراجعة #15: المقارنة في الجملة وما يليها فقط؛ «النهار/الليل» بينهما جمل كثيرة فلا طباق ولا مقابلة
        t = ("خرج القوم من المدينة في أول النهار، وساروا في الطريق الطويل حتى بلغوا الوادي، فنزلوا عند البئر وسقوا إبلهم، "
             "ثم جلسوا يتحدثون عن أخبار السوق، ولما جاء الليل ناموا حتى الصباح")
        self.assertNotIn(("النهار", "الليل"), {tuple(x["اللفظان"]) for x in found(t, "الطباق")})
        self.assertEqual(found(t, "المقابلة"), [])

    def test_general_antonyms(self):
        # المهمة 14: «يفني/يبقي» من قائمة الأضداد العامة (ويكاموس، الطبقة A)، والمقابلة في بغية الإيضاح ج4
        m = found("فلا الجود يفني المال والجد مقبل * ولا البخل يبقي المال والجد مدبر", "المقابلة")
        self.assertIn(["يفني", "يبقي"], m[0]["الأزواج"] if m else [])
        # فخّ الترديد (تحرير التحبير ص255) لا طباق فيه بالطبقة الافتراضية (A)
        self.assertEqual(found("قل لمن ساد ثم ساد أبوه * قبله ثم قبل ذلك جده", "الطباق"), [])


if __name__ == "__main__":
    unittest.main()
