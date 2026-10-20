from app.rag.arabic import fix_lam_alef


def test_fixes_swapped_lam_alef_after_article():
    assert fix_lam_alef("اإلجارة") == "الإجارة"
    assert fix_lam_alef("الحد األدنى") == "الحد الأدنى"
    assert fix_lam_alef("الحد االدنى") == "الحد الادنى"


def test_leaves_correct_text_unchanged():
    assert fix_lam_alef("التمويل السكني") == "التمويل السكني"
