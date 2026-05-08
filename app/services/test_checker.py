import json


UNANSWERED_SYMBOL = "-"


def check_test_answers(answer_key: str, student_answers: str) -> dict:
    correct_count = 0
    wrong_count = 0
    details = []

    answer_key = answer_key.upper()
    student_answers = student_answers.upper()

    for index, correct_answer in enumerate(answer_key):
        if index < len(student_answers):
            student_answer = student_answers[index]
        else:
            student_answer = UNANSWERED_SYMBOL

        is_correct = correct_answer == student_answer

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        details.append(
            {
                "question": index + 1,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "is_unanswered": student_answer == UNANSWERED_SYMBOL,
            }
        )

    total = len(answer_key)
    percentage = round((correct_count / total) * 100, 1) if total > 0 else 0

    return {
        "total": total,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "percentage": percentage,
        "details": details,
    }


def details_to_json(details: list[dict]) -> str:
    return json.dumps(details, ensure_ascii=False)


def details_from_json(value: str) -> list[dict]:
    return json.loads(value)


def build_student_result_text(
    full_name: str,
    test_code: str,
    result: dict,
    is_timeout: bool = False,
) -> str:
    details = result["details"]

    title = "⏰ <b>Vaqt tugadi. Test avtomatik yakunlandi.</b>" if is_timeout else "✅ <b>Test natijasi tayyor</b>"

    lines = [
        title,
        "",
        f"👤 <b>O‘quvchi:</b> {full_name}",
        f"🧪 <b>Test kodi:</b> {test_code}",
        "",
        f"📌 <b>Jami savol:</b> {result['total']} ta",
        f"✅ <b>To‘g‘ri:</b> {result['correct_count']} ta",
        f"❌ <b>Xato:</b> {result['wrong_count']} ta",
        f"📊 <b>Foiz:</b> {result['percentage']}%",
        "",
        "📋 <b>O‘quvchi javoblari:</b>",
    ]

    for item in details:
        icon = "✅" if item["is_correct"] else "❌"

        if item.get("is_unanswered"):
            student_answer_text = "javob berilmagan"
        else:
            student_answer_text = item["student_answer"]

        lines.append(
            f"{item['question']}-savol: {student_answer_text} {icon}"
        )

    wrong_items = [item for item in details if not item["is_correct"]]

    if wrong_items:
        lines.append("")
        lines.append("❌ <b>Xato javoblar tafsiloti:</b>")

        for item in wrong_items:
            if item.get("is_unanswered"):
                lines.append(
                    f"{item['question']}-savol: javob berilmagan, "
                    f"to‘g‘ri javob {item['correct_answer']}"
                )
            else:
                lines.append(
                    f"{item['question']}-savol: "
                    f"siz {item['student_answer']} deb javob berdingiz, "
                    f"to‘g‘ri javob {item['correct_answer']}"
                )

    return "\n".join(lines)