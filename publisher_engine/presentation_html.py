import html
from pathlib import Path
import json


def _text(value):
    if value is None:
        return ""

    return str(value).strip()


def load_presentation_urls(
        build_root,
        build_name,
        slides=None
):
    slides = slides or {}

    slides_folder = (
        Path(build_root)
        / "Slides"
        / build_name
    )

    urls_file = (
        slides_folder
        / "slides_urls.json"
    )

    data = {}

    if urls_file.is_file():
        loaded = json.loads(
            urls_file.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(loaded, dict):
            data = loaded

    presentation_url = _text(
        data.get("presentation_url")
    )

    pptx_url = _text(
        data.get("pptx_url")
    )

    if not presentation_url:
        presentation_url = _text(
            slides.get("gamma_slides_url")
            or slides.get("presentation_url")
        )

    if not pptx_url:
        pptx_url = _text(
            slides.get("pptx_url")
        )

    return {
        "presentation_url":
            presentation_url,

        "pptx_url":
            pptx_url,
    }


def build_presentation_html(
        build_root,
        build_name,
        slides=None
):
    urls = load_presentation_urls(
        build_root,
        build_name,
        slides=slides,
    )

    presentation_url = urls[
        "presentation_url"
    ]

    pptx_url = urls[
        "pptx_url"
    ]

    if not presentation_url and not pptx_url:
        return ""

    parts = [
        '<div class="rono-presentation-launcher">',
        '<p>'
        'Open the interactive lesson presentation '
        'in a new tab.'
        '</p>',
        '<p>',
    ]

    if presentation_url:
        safe_url = html.escape(
            presentation_url,
            quote=True
        )

        parts.append(
            '<a '
            f'href="{safe_url}" '
            'target="_blank" '
            'rel="noopener noreferrer" '
            'style="'
            'display:inline-block;'
            'padding:12px 18px;'
            'margin:0 10px 10px 0;'
            'border:1px solid #555;'
            'border-radius:6px;'
            'text-decoration:none;'
            'font-weight:600;'
            '">'
            'Open Presentation'
            '</a>'
        )

    if pptx_url:
        safe_pptx = html.escape(
            pptx_url,
            quote=True
        )

        parts.append(
            '<a '
            f'href="{safe_pptx}" '
            'target="_blank" '
            'rel="noopener noreferrer" '
            'style="'
            'display:inline-block;'
            'padding:12px 18px;'
            'margin:0 10px 10px 0;'
            'border:1px solid #555;'
            'border-radius:6px;'
            'text-decoration:none;'
            'font-weight:600;'
            '">'
            'Download PowerPoint'
            '</a>'
        )

    parts.extend([
        '</p>',
        '</div>',
    ])

    return "".join(parts)
