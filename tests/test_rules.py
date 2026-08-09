from question_audit.rules import aggregate_passes, hard_gate


def p(letter,conf=.9,door="poder",flags=None):
    return {"answer_letter":letter,"confidence":conf,"door_id":door,"subtopic":"Estado","flags":flags or []}


def test_unanimous_high_confidence_auto_ready():
    out=aggregate_passes([p("D"),p("D",.88),p("D",.92)],.80,.65)
    assert out["status"]=="AUTO_READY"
    assert out["answer_letter"]=="D"


def test_majority_goes_review():
    out=aggregate_passes([p("D"),p("D"),p("B")],.80,.65)
    assert out["status"]=="REVIEW"
    assert out["answer_letter"]=="D"


def test_serious_flag_blocks_auto():
    out=aggregate_passes([p("A",flags=["ambiguous_question"]),p("A"),p("A")],.80,.65)
    assert out["status"]=="REVIEW"


def test_cancelled_is_hold():
    q={"is_canceled":True,"answer_type":"MULTIPLE_CHOICE","alternatives":[1,2,3,4],"statement_html":"x"}
    status,flags=hard_gate(q)
    assert status=="HOLD"
    assert "source_marked_cancelled" in flags
