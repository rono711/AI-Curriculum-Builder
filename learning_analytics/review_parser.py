"""Extract diagnostic evidence from Moodle quiz review HTML."""

import html as html_lib

from bs4 import BeautifulSoup


def clean_text(value):
    if value is None:
        return None

    value = html_lib.unescape(str(value))

    return " ".join(
        value.split()
    ).strip()


def question_text(soup):
    node = soup.select_one(
        ".qtext"
    )

    if not node:
        return None

    return clean_text(
        node.get_text(
            " ",
            strip=True
        )
    )


def correct_answer(soup):
    node = soup.select_one(
        ".rightanswer"
    )

    if not node:
        return None

    text = clean_text(
        node.get_text(
            " ",
            strip=True
        )
    )

    prefix = "The correct answer is:"

    if (
        text
        and text.lower().startswith(
            prefix.lower()
        )
    ):
        text = text[
            len(prefix):
        ].strip()

    return text


def multichoice_response(soup):
    checked = soup.select_one(
        'input[type="radio"][checked]'
    )

    if not checked:
        return None

    input_id = checked.get(
        "id"
    )

    if not input_id:
        return None

    label = soup.find(
        id=f"{input_id}_label"
    )

    if not label:
        return None

    answer_number = label.select_one(
        ".answernumber"
    )

    if answer_number:
        answer_number.extract()

    icon = label.select_one(
        "i"
    )

    if icon:
        icon.extract()

    return clean_text(
        label.get_text(
            " ",
            strip=True
        )
    )


def shortanswer_response(soup):
    node = soup.select_one(
        'input[type="text"][name$="_answer"]'
    )

    if not node:
        return None

    return clean_text(
        node.get(
            "value",
            ""
        )
    )


def match_response(soup):
    pairs = []

    for row in soup.select(
        "table.answer tr"
    ):
        stem = row.select_one(
            "td.text"
        )

        selected = row.select_one(
            "select option[selected]"
        )

        if not stem or not selected:
            continue

        left = clean_text(
            stem.get_text(
                " ",
                strip=True
            )
        )

        right = clean_text(
            selected.get_text(
                " ",
                strip=True
            )
        )

        if (
            left
            and right
            and right != "Choose..."
        ):
            pairs.append(
                f"{left} -> {right}"
            )

    if not pairs:
        return None

    return "; ".join(
        pairs
    )


def generic_saved_response(soup):
    rows = soup.select(
        ".history table tbody tr"
    )

    for row in rows:
        cells = row.select(
            "td"
        )

        if len(cells) < 3:
            continue

        action = clean_text(
            cells[2].get_text(
                " ",
                strip=True
            )
        )

        if (
            action
            and action.startswith(
                "Saved:"
            )
        ):
            return action[
                len("Saved:"):
            ].strip()

    return None


def parse_question(question):
    html = question.get(
        "html",
        ""
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    qtype = str(
        question.get(
            "type",
            ""
        )
    )

    if qtype == "multichoice":
        student_response = (
            multichoice_response(
                soup
            )
        )

    elif qtype == "shortanswer":
        student_response = (
            shortanswer_response(
                soup
            )
        )

    elif qtype == "match":
        student_response = (
            match_response(
                soup
            )
        )

    else:
        student_response = None

    if not student_response:
        student_response = (
            generic_saved_response(
                soup
            )
        )

    return {
        "slot":
            int(
                question.get(
                    "slot",
                    0
                )
            ),

        "question_type":
            qtype,

        "status":
            clean_text(
                question.get(
                    "status"
                )
            ),

        "mark":
            float(
                question.get(
                    "mark",
                    0
                )
                or 0
            ),

        "max_mark":
            float(
                question.get(
                    "maxmark",
                    0
                )
                or 0
            ),

        "question_text":
            question_text(
                soup
            ),

        "student_response":
            student_response,

        "correct_response":
            correct_answer(
                soup
            ),
    }
