"""Testy pro výpočet náhledových obdélníků."""
from video_collage.layout import calculate_slot_rectangles
from video_collage.templates import Template, TemplateSlot


def test_calculate_rectangles_basic_grid() -> None:
    template = Template(
        template_id="t1",
        name="Test",
        rows=2,
        columns=2,
        slots=[
            TemplateSlot("A", 0, 0),
            TemplateSlot("B", 0, 1),
            TemplateSlot("C", 1, 0),
            TemplateSlot("D", 1, 1),
        ],
    )
    rectangles = calculate_slot_rectangles(template, width=200, height=100)
    assert rectangles["A"] == (0.0, 0.0, 100.0, 50.0)
    assert rectangles["D"] == (100.0, 50.0, 200.0, 100.0)


def test_calculate_rectangles_with_spans() -> None:
    template = Template(
        template_id="t2",
        name="Span",
        rows=3,
        columns=3,
        slots=[
            TemplateSlot("A", 0, 0, row_span=2, column_span=2),
            TemplateSlot("B", 0, 2, row_span=3, column_span=1),
            TemplateSlot("C", 2, 0, row_span=1, column_span=2),
        ],
    )
    rectangles = calculate_slot_rectangles(template, width=300, height=300)
    assert rectangles["A"] == (0.0, 0.0, 200.0, 200.0)
    assert rectangles["B"] == (200.0, 0.0, 300.0, 300.0)
    assert rectangles["C"] == (0.0, 200.0, 200.0, 300.0)


def test_invalid_dimensions_raise_value_error() -> None:
    template = Template(
        template_id="t3",
        name="Invalid",
        rows=1,
        columns=1,
        slots=[TemplateSlot("A", 0, 0)],
    )
    try:
        calculate_slot_rectangles(template, width=0, height=100)
    except ValueError as exc:
        assert "kladné" in str(exc)
    else:  # pragma: no cover - selhání testu
        raise AssertionError("Nezachycena ValueError pro neplatné rozměry")

