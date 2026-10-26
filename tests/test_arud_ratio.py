# -*- coding: utf-8 -*-
"""نسبة التشكيل في `_prepare_verse_text0`: البيت التام الضبط لا يُعاد ضبطه آليًّا، والناقص يُكمَل.

لا يدخل مقامَ النسبة ما لا يحمل حركةً في الضبط التام (قائمة سقط الزند): ألف المد وألف «ال» وهمزة الوصل،
وواو المد وياؤه، واللام الشمسية قبل المشدَّد، والألف الفارقة، والألف المقصورة.
والأبيات من سقط الزند لأبي العلاء المعري: ثلاثة بضبط المصدر، وسبعة عشر أتمّ ضبطها المراجع."""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sarf_mcp as M

# مشكولة من المصدر
SOURCE_VOWELLED = [
    "غَيْرُ مُجْدٍ فِي مِلَّتِي وَاعْتِقَادِي * نَوْحُ بَاكٍ وَلَا تَرَنُّمُ شَادِ",
    "خَفِّفِ الْوَطْءَ مَا أَظُنُّ أَدِيمَ الْ * أَرْضِ إِلَّا مِنْ هَذِهِ الْأَجْسَادِ",
    "رُبَّ لَحْدٍ قَدْ صَارَ لَحْدًا مِرَارًا * ضَاحِكٍ مِنْ تَزَاحُمِ الْأَضْدَادِ",
]

# أتمّ المراجع ضبطها
REVIEWER_VOWELLED = [
    "أَلَا فِي سَبِيلِ المَجْدِ مَا أَنَا فَاعِلُ * عَفَافٌ وَإِقْدَامٌ وَحَزْمٌ وَنَائِلُ",
    "وَإِنِّي وَإِنْ كُنْتُ الأَخِيرَ زَمَانُهُ * لَآتٍ بِمَا لَمْ تَسْتَطِعْهُ الأَوَائِلُ",
    "وَلَمَّا رَأَيْتُ الجَهْلَ فِي النَّاسِ فَاشِيًا * تَجَاهَلْتُ حَتَّى ظُنَّ أَنِّيَ جَاهِلُ",
    "لَقَدْ آنَ أَنْ يَثْنِي الجَمُوحَ لِجَامُ * وَأَنْ يَمْلِكَ الصَّعْبَ الأَبِيَّ ذِمَامُ",
    "خُلُوُّ فُؤَادِي بِالمَوَدَّةِ إِخْلَالُ * وَإِبْلَاءُ جِسْمِي فِي طِلَابِكِ إِبْلَالُ",
    "يَا سَاهِرَ البَرْقِ أَيْقِظْ رَاقِدَ السَّمُرِ * لَعَلَّ بِالجِزْعِ أَعْوَانًا عَلَى السَّهَرِ",
    "فَالحُسْنُ يَظْهَرُ فِي شَيْئَيْنِ رَوْنَقُهُ * بَيْتٍ مِنَ الشِّعْرِ أَوْ بَيْتٍ مِنَ الشَّعَرِ",
    "هَاتِ الحَدِيثَ عَنِ الزَّوْرَاءِ أَوْ هِيتَا * وَمُوقَدِ النَّارِ لَا تَكْرَى بِتَكْرِيتَا",
    "أَدْنَى الفَوَارِسِ مَنْ يُغِيرُ لِمَغْنَمِ * فَاجْعَلْ مُغَارَكَ لِلْمَكَارِمِ تُكْرَمِ",
    "أَوْدَى فَلَيْتَ الحَادِثَاتِ كَفَافِ * مَالُ المُسِيفِ وَعَنْبَرُ المُسْتَافِ",
    "أَعَنْ وَخْدِ القِلَاصِ كَشَفْتِ حَالَا * وَمِنْ عِنْدِ الظَّلَامِ طَلَبْتِ مَالَا",
    "أَرَى العَنْقَاءَ تَكْبُرُ أَنْ تُصَادَا * فَعَانِدْ مَنْ تُطِيقُ لَهُ عِنَادَا",
    "عَلِّلَانِي فَإِنَّ بِيضَ الأَمَانِي * فَنِيَتْ وَالظَّلَامُ لَيْسَ بِفَانِي",
    "أَحْسَنُ بِالوَاجِدِ مِنْ وَجْدِهِ * صَبْرٌ يُعِيدُ النَّارَ فِي زَنْدِهِ",
    "أَهَاجَكَ البَرْقُ بِذَاتِ الأَمْعَزِ * بَيْنَ الصَّرَاةِ وَالفُرَاتِ يَجْتَزِي",
    "تُثْنِي عَلَيْكَ البِلَادُ أَنَّكَ لَا * تَأْخُذُ مِنْ رِفْدِهَا وَتَرْفِدُهَا",
    "تَوَقَّتْكَ سِرًّا وَزَارَتْ جِهَارَا * وَهَلْ تَطْلُعُ الشَّمْسُ إِلَّا نَهَارَا",
]


def _strip_every_other_word(text):
    return " ".join(M._strip_tashkeel(w) if i % 2 else w for i, w in enumerate(text.split()))


class TestFullyVowelledNotRevowelled(unittest.TestCase):
    def _assert_kept(self, verses):
        for v in verses:
            with self.subTest(v=v), mock.patch.object(M, "_diacritize_verse", side_effect=AssertionError("أُعيد ضبطه")):
                self.assertGreaterEqual(M._tashkeel_ratio(v), 0.85)
                self.assertEqual(M._prepare_verse_text0(v), (v, None))

    def test_source_vowelled(self):
        self.assertEqual(len(SOURCE_VOWELLED), 3)
        self._assert_kept(SOURCE_VOWELLED)

    def test_reviewer_vowelled(self):
        self.assertEqual(len(REVIEWER_VOWELLED), 17)
        self._assert_kept(REVIEWER_VOWELLED)


class TestUnderVowelledCompleted(unittest.TestCase):
    def test_stripped_verse_fully_diacritized(self):
        bare = M._strip_tashkeel(REVIEWER_VOWELLED[0])
        self.assertLess(M._tashkeel_ratio(bare), 0.3)
        with mock.patch.object(M, "_diacritize_verse", return_value="مشكول") as d:
            t, note = M._prepare_verse_text0(bare)
        d.assert_called_once_with(bare)
        self.assertEqual((t, note), ("مشكول", "البيت غير مشكول فشُكِّل آليًّا."))

    def test_half_vowelled_verse_completed(self):
        half = _strip_every_other_word(REVIEWER_VOWELLED[0])
        r = M._tashkeel_ratio(half)
        self.assertTrue(0.3 <= r < 0.85, r)
        with mock.patch.object(M, "_diacritize_verse", side_effect=lambda t: t) as d:
            _t, note = M._prepare_verse_text0(half)
        d.assert_called_once()
        self.assertEqual(note, "التشكيل ناقص فأُكمل آليًّا مع إبقاء ضبط الأصل.")


class TestExcludedLetters(unittest.TestCase):
    # كل كلمة هنا تامة الضبط، فنسبتها 1، وكانت دون ذلك في الحساب القديم
    def test_each_rule(self):
        for w in ("كِتَابٌ",          # (1) ألف المد بعد فتحة
                  "بِالْمَوَدَّةِ",    # (1) ألف «ال» بعد سابقة
                  "ابْنُ",             # (1) همزة الوصل بلا همزة
                  "يَقُولُ", "فِيهِ",  # (2) واو المد وياؤه
                  "الشَّمْسُ",         # (3) اللام الشمسية
                  "كَتَبُوا",          # (4) الألف الفارقة
                  "عَلَى"):            # (5) الألف المقصورة
            with self.subTest(w=w):
                self.assertEqual(M._tashkeel_ratio(w), 1.0)

    def test_carrying_letters_still_count(self):
        # اللام القمرية بلا سكون حرفٌ يُشكل، فتنقص به النسبة
        self.assertLess(M._tashkeel_ratio("القَمَرُ"), 1.0)


if __name__ == "__main__":
    unittest.main()
