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

    def test_hamza_kept_in_makharij(self):
        # مراجعة #15، الدورة 1 (badi-005، جواهر البلاغة ص327): «ينهون/ينأون» الهاء والهمزة متقاربتان، فهو مضارع لا لاحق
        self.assertIn((("ينهون", "وينأون"), "جناس مضارع"), jinas("وهم ينهون عنه، وينأون عنه"))

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


# جمل بليغ العادية العشر (مراجعة #15، /workspace/review15/spot/cases.json): لا بديع فيها
ORDINARY = {
    "P1": "ذهب الطالب إلى المدرسة صباحا وقرأ درسه في المكتبة ثم عاد إلى بيته",
    "P2": "اشترى أبي سيارة جديدة من المعرض، ودفع ثمنها نقدا، ثم أخذنا في نزهة إلى البحر",
    "P3": "يعمل الفلاحون في الحقول منذ الفجر، ويسقون الزرع، ويجمعون الثمر قبل الغروب",
    "P4": "كتب المؤلف هذا الكتاب في ثلاث سنين، وجمع فيه أخبار العلماء ورحلاتهم إلى المدن",
    "P5": "قال المعلم للتلاميذ افتحوا كتبكم على الصفحة العاشرة واقرؤوا الفقرة الأولى بصوت واضح",
    "P6": "وصل الوفد إلى المطار مساء الخميس، واستقبله الوزير، ثم انتقل إلى الفندق القريب من السوق",
    "P7": "أقيموا بني أمي صدور مطيكم * فإني إلى قوم سواكم لأميل",
    "P8": "ولما رأيت الجهل في الناس فاشيا * تجاهلت حتى ظن أني جاهل",
    "P9": "العيد قريب، والناس يشترون الملابس والحلوى للأطفال",
    "P10": "ركب الرجل الكريم الخيل وخرج إلى الصيد مع أصحابه",
}
# رصود سابقة على #15 (موجودة على main قبله) لم تُعالَج في هذه المراجعة: حدود معروفة
ORDINARY_KNOWN = {"P1": "جناس ناقص المدرسة/درسه (من جذر واحد)", "P4": "سجع سنين/المدن",
                  "P7": "جناس لاحق بني/فإني وأمي/فإني", "P8": "جناس الاشتقاق الجهل/تجاهلت/جاهل وردّ العجز (يحكم فيه بليغ)"}


class TestOrdinarySentences(unittest.TestCase):
    def test_no_tibaq_or_muqabala(self):
        for k, t in ORDINARY.items():
            with self.subTest(k):
                self.assertEqual((found(t, "الطباق"), found(t, "المقابلة")), ([], []))

    def test_no_badi_at_all(self):
        for k, t in ORDINARY.items():
            if k in ORDINARY_KNOWN:
                continue
            with self.subTest(k):
                self.assertIsInstance(M.detect_badi(t)["المحسنات"], str)

    @unittest.expectedFailure
    def test_no_badi_known_limits(self):
        for k in ORDINARY_KNOWN:
            self.assertIsInstance(M.detect_badi(ORDINARY[k])["المحسنات"], str, k)


class TestShaddaHayah(unittest.TestCase):
    def test_bughya_643_shadda(self):
        # منقول: بغية الإيضاح ج4 ص643، باب الجناس المحرّف، عن السكاكي: «الجهول إما مفرِط أو مفرِّط»،
        # «والمشدد في هذا الباب يقوم مقام المخفف نظرًا إلى الصورة»: الشدة لا تُعدّ حرفًا، لكنها تغيّر الهيئة
        self.assertIn((("مُفْرِط", "مُفَرِّط"), "جناس محرّف"), jinas("الجهول إما مُفْرِط أو مُفَرِّط"))
        self.assertIn((("مفرِط", "مفرِّط"), "جناس محرّف"), jinas("الجهول إما مفرِط أو مفرِّط"))
        self.assertIn((("قَدَر", "وقَدَّر"), "جناس محرّف"), jinas("قَدَر الله وقَدَّر"))


class TestShortWords(unittest.TestCase):
    def test_jadd_jidd(self):
        # مراجعة #15: الكلمة القصيرة تُرصد محرّفًا إذا ضُبطت الكلمتان وحروفهما واحدة والاختلاف في الحركات وحدها
        self.assertIn((("الجَدّ", "الجِدّ"), "جناس محرّف"), jinas("الجَدّ في الجِدّ"))
        # وبلا ضبط لا يُرصد شيء في الكلمة القصيرة
        self.assertEqual(jinas("الجد في الجد"), set())

    def test_tam_needs_matching_diacritization(self):
        # إذا ضُبطت إحدى الكلمتين دون الأخرى فلا يُقطع بالجناس التام، وإنما يُذكر «جناس محتمل»
        # (اللمّة تُجعل اللفظ نفسه هنا ليختلف المعنى، فيُختبر حكم الضبط وحده)
        from unittest import mock
        with mock.patch.object(M, "_lemma_bare", lambda w: w):
            mixed = {k for _, k in jinas("نظرت إلى العَيْن عند العين")}
            plain = {k for _, k in jinas("نظرت إلى عين عند العين")}
        self.assertEqual((("جناس تام" in mixed), ("جناس محتمل" in mixed)), (False, True))
        self.assertIn("جناس تام", plain)


class TestAntonymFile(unittest.TestCase):
    def test_missing_file_warns(self):
        # مراجعة #15: غياب data/badi/antonyms_general.tsv لا يُسكت عنه
        import io, contextlib
        old = M._ANTONYMS_TSV
        try:
            M._ANTONYMS_TSV = "/nonexistent/antonyms_general.tsv"
            M._antonym_index.cache_clear()
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                r = M.detect_badi("ليل ونهار")
            self.assertIn("قائمة الأضداد العامة", err.getvalue())
            self.assertIn("تنبيه", r)
        finally:
            M._ANTONYMS_TSV = old; M._ANTONYM_FILE_WARNING = None
            M._antonym_index.cache_clear()


if __name__ == "__main__":
    unittest.main()
