"""Executive decision-brief PDF export for the active SAGE research report.

Produces a concise (~4-6 page) consulting-style brief distilled from the same
report data the app renders — not a dump of every record. Detailed evidence,
source records and research methodology remain available in the SAGE app and
the JSON export.
"""

import re
from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import (
    CondPageBreak,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from evidence_intelligence import (
    build_evidence_intelligence,
    build_validation_intelligence,
    derive_market_chart_data,
    derive_single_period_chart_data,
)


# Editorial ink-and-brass palette — echoes the SAGE product's visual identity.
INK = colors.HexColor("#221d16")
INK_SOFT = colors.HexColor("#4a4335")
BRASS = colors.HexColor("#9c6b2e")
TEAL = colors.HexColor("#2f6f5e")
TERRACOTTA = colors.HexColor("#a1503a")
MUTED = colors.HexColor("#7a7261")
RULE = colors.HexColor("#e3dbc9")
PALE = colors.HexColor("#f7f2e7")

CONTENT_WIDTH = letter[0] - 1.44 * inch

MAIN_KEYS = (
    "finding", "insight", "title", "name", "pattern", "characteristic",
    "development", "trend", "point", "statement", "description", "text",
    "summary", "segment", "competitor", "opportunity", "risk", "action",
    "implication", "recommendation",
)


def _register_font_pair():
    candidates = (
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
        (Path(__import__("reportlab").__file__).parent / "fonts/Vera.ttf", Path(__import__("reportlab").__file__).parent / "fonts/VeraBd.ttf"),
    )
    for regular, bold in candidates:
        if not regular.is_file() or not bold.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont("SAGEUnicode", str(regular)))
            pdfmetrics.registerFont(TTFont("SAGEUnicode-Bold", str(bold)))
            return "SAGEUnicode", "SAGEUnicode-Bold"
        except Exception:
            continue
    return "Helvetica", "Helvetica-Bold"


def _empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, dict):
        return not any(not _empty(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return not any(not _empty(item) for item in value)
    return False


def _text(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def _norm(key):
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def _lookup(item, keys):
    """Return the first non-empty value in `item` matching one of the normalized `keys`."""
    if not isinstance(item, dict):
        return None
    table = {}
    for key, value in item.items():
        table.setdefault(_norm(key), value)
    for key in keys:
        value = table.get(key)
        if not _empty(value):
            return value
    return None


def _flatten(value, limit=None):
    """Flatten any structure into a short readable string (never a Python repr)."""
    if _empty(value):
        return ""
    if isinstance(value, str):
        text = value.strip()
    elif isinstance(value, (int, float, bool)):
        text = _text(value)
    elif isinstance(value, (list, tuple)):
        text = "; ".join(_flatten(v) for v in value if not _empty(v))
    elif isinstance(value, dict):
        main = _lookup(value, MAIN_KEYS)
        if main is not None:
            text = _flatten(main)
        else:
            text = " | ".join(
                f"{k.replace('_', ' ').capitalize()}: {_flatten(v)}"
                for k, v in value.items() if not _empty(v)
            )
    else:
        text = str(value)
    if limit and len(text) > limit:
        text = text[:limit].rstrip() + "\u2026"
    return text


def _as_list(value):
    if _empty(value):
        return []
    if isinstance(value, (list, tuple)):
        return [v for v in value if not _empty(v)]
    return [value]


def _top(value, n):
    return _as_list(value)[:n]


def _paragraph(text, style, link=None):
    text = _text(text)
    text = "".join(character if character in "\t\n\r" or ord(character) >= 32 else " " for character in text)
    text = text.encode("utf-8", errors="replace").decode("utf-8")
    safe_text = escape(text).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
    if link:
        safe_link = escape(link, {"\"": "&quot;"})
        safe_text = f'<link href="{safe_link}" color="#9c6b2e">{safe_text}</link>'
    return Paragraph(safe_text, style)


def _rich(xml_body, style):
    """Render pre-built XML markup (caller has already escaped dynamic parts)."""
    return Paragraph(xml_body, style)


def _kicker(text, styles):
    return Paragraph(escape(str(text).upper()), styles["Kicker"])


def _rule(space_before=2, space_after=10):
    return HRFlowable(width="100%", thickness=0.7, color=RULE, spaceBefore=space_before, spaceAfter=space_after)


def _strength_word(value):
    text = _flatten(value).lower()
    if not text or len(text) > 40:
        return None
    if "strong" in text or "high" in text or "robust" in text:
        return "Strong evidence"
    if "moderate" in text or "medium" in text or "mixed" in text:
        return "Moderate evidence"
    if "weak" in text or "low" in text or "limited" in text:
        return "Limited evidence"
    return None


def _finding_block(item, styles):
    main = _flatten(_lookup(item, ("finding", "key_finding", "insight", "title", "statement", "description")) or item, limit=280)
    why = _flatten(_lookup(item, ("why_it_matters", "why_matters", "significance", "importance", "business_meaning", "implication")), limit=220)
    strength = _strength_word(_lookup(item, ("evidence_strength", "strength", "evidence_level", "confidence")))
    flow = [_paragraph(main, styles["LeadItem"])]
    if why:
        flow.append(_paragraph(why, styles["Meta"]))
    if strength:
        flow.append(_paragraph(strength.upper(), styles["Tag"]))
    flow.append(Spacer(1, 8))
    return KeepTogether(flow)


def _signal_block(item, styles):
    title = _flatten(_lookup(item, ("title", "opportunity", "risk", "name", "headline", "finding")) or item, limit=180)
    detail = _flatten(_lookup(item, ("explanation", "description", "why_it_matters", "rationale", "business_meaning", "mitigation")), limit=220)
    flow = [_paragraph(title, styles["ItemTitle"])]
    if detail:
        flow.append(_paragraph(detail, styles["Meta"]))
    flow.append(Spacer(1, 7))
    return flow


def _action_block(item, index, styles):
    action = _flatten(_lookup(item, ("action", "recommendation", "recommended_action", "title", "step", "initiative")) or item, limit=200)
    impact = _flatten(_lookup(item, ("expected_business_impact", "expected_impact", "business_impact", "impact", "expected_outcome", "benefit")), limit=180)
    priority = _flatten(_lookup(item, ("priority",)), limit=20)
    flow = [_rich(f"{index:02d}&nbsp;&nbsp;{escape(action)}", styles["ItemTitle"])]
    if priority:
        flow.append(_paragraph(f"PRIORITY {priority}".upper(), styles["Tag"]))
    if impact:
        flow.append(_paragraph(f"Expected impact: {impact}", styles["Meta"]))
    flow.append(Spacer(1, 8))
    return KeepTogether(flow)


def _mini_chart(chart_data):
    if not isinstance(chart_data, dict):
        return None
    labels = chart_data.get("labels") or []
    values = chart_data.get("values") or []
    if len(labels) < 2 or len(labels) != len(values):
        return None
    labels = [str(label)[:14] for label in labels[:8]]
    values = list(values[:8])

    drawing = Drawing(CONTENT_WIDTH, 150)
    chart = VerticalBarChart()
    chart.x = 34
    chart.y = 26
    chart.width = CONTENT_WIDTH - 50
    chart.height = 105
    chart.data = [values]
    chart.categoryAxis.categoryNames = labels
    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.fillColor = MUTED
    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.labels.fillColor = MUTED
    chart.valueAxis.valueMin = 0
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = RULE
    chart.valueAxis.strokeColor = RULE
    chart.categoryAxis.strokeColor = RULE
    chart.bars[0].fillColor = BRASS
    chart.barWidth = 10
    chart.groupSpacing = 8
    drawing.add(chart)
    return drawing


def _draw_page(canvas, document, regular_font, bold_font, generated):
    canvas.saveState()
    page_width, page_height = document.pagesize
    canvas.setFillColor(MUTED)
    canvas.setFont(bold_font, 7.5)
    canvas.drawString(document.leftMargin, page_height - 0.48 * inch, "SAGE  /  EXECUTIVE DECISION BRIEF")
    if generated:
        canvas.setFont(regular_font, 7.5)
        canvas.drawRightString(page_width - document.rightMargin, page_height - 0.48 * inch, generated)
    canvas.setStrokeColor(BRASS)
    canvas.setLineWidth(1.1)
    canvas.line(document.leftMargin, page_height - 0.58 * inch, document.leftMargin + 0.55 * inch, page_height - 0.58 * inch)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(document.leftMargin, 0.55 * inch, page_width - document.rightMargin, 0.55 * inch)
    canvas.setFont(regular_font, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(document.leftMargin, 0.36 * inch, "Distilled by SAGE \u2014 full evidence and sources available in the workspace")
    canvas.drawRightString(page_width - document.rightMargin, 0.36 * inch, f"Page {document.page}")
    canvas.restoreState()


def build_research_pdf(brief, report):
    """Return a concise executive decision-brief PDF for an already-loaded SAGE report."""
    brief = brief if isinstance(brief, dict) else {}
    report = report if isinstance(report, dict) else {}

    intelligence = report.get("evidence_intelligence")
    if not isinstance(intelligence, dict) or not all(
        key in intelligence for key in ("items", "sources", "evidence_gaps", "research_limitations", "quality_assessment")
    ):
        intelligence = build_evidence_intelligence(
            report.get("research_evidence"),
            report.get("business_intelligence"),
            report.get("strategic_synthesis"),
        )

    validation = report.get("validation_intelligence")
    if not isinstance(validation, dict):
        validation = build_validation_intelligence(report)

    regular_font, bold_font = _register_font_pair()
    stylesheet = getSampleStyleSheet()
    styles = {
        "Body": ParagraphStyle(
            "SAGEBody", parent=stylesheet["BodyText"], fontName=regular_font,
            fontSize=9.5, leading=14.5, textColor=INK_SOFT, spaceAfter=6, wordWrap="CJK",
        ),
        "Kicker": ParagraphStyle(
            "SAGEKicker", parent=stylesheet["BodyText"], fontName=bold_font,
            fontSize=8, leading=11, textColor=BRASS, spaceBefore=14, spaceAfter=4,
            wordWrap="CJK",
        ),
        "Section": ParagraphStyle(
            "SAGESection", parent=stylesheet["Heading1"], fontName="Times-Bold",
            fontSize=17, leading=21, textColor=INK, spaceBefore=2, spaceAfter=8,
            keepWithNext=True,
        ),
        "LeadItem": ParagraphStyle(
            "SAGELeadItem", parent=stylesheet["BodyText"], fontName="Times-Bold",
            fontSize=12, leading=16.5, textColor=INK, spaceAfter=3, wordWrap="CJK",
        ),
        "ItemTitle": ParagraphStyle(
            "SAGEItemTitle", parent=stylesheet["BodyText"], fontName=bold_font,
            fontSize=10, leading=13.5, textColor=INK, spaceAfter=2, wordWrap="CJK",
        ),
        "Meta": ParagraphStyle(
            "SAGEMeta", parent=stylesheet["BodyText"], fontName=regular_font,
            fontSize=9, leading=13, textColor=INK_SOFT, spaceAfter=3, wordWrap="CJK",
        ),
        "Tag": ParagraphStyle(
            "SAGETag", parent=stylesheet["BodyText"], fontName=bold_font,
            fontSize=6.8, leading=9, textColor=TEAL, spaceAfter=4, wordWrap="CJK",
        ),
        "Quote": ParagraphStyle(
            "SAGEQuote", parent=stylesheet["BodyText"], fontName="Times-Bold",
            fontSize=14, leading=20, textColor=INK, wordWrap="CJK",
        ),
        "StatValue": ParagraphStyle(
            "SAGEStatValue", parent=stylesheet["BodyText"], fontName="Times-Bold",
            fontSize=19, leading=22, textColor=INK, alignment=TA_LEFT,
        ),
        "StatLabel": ParagraphStyle(
            "SAGEStatLabel", parent=stylesheet["BodyText"], fontName=bold_font,
            fontSize=6.8, leading=9, textColor=MUTED,
        ),
        "ColHead": ParagraphStyle(
            "SAGEColHead", parent=stylesheet["BodyText"], fontName="Times-Bold",
            fontSize=12.5, leading=15, textColor=TEAL, spaceAfter=6,
        ),
        "ColHeadRisk": ParagraphStyle(
            "SAGEColHeadRisk", parent=stylesheet["BodyText"], fontName="Times-Bold",
            fontSize=12.5, leading=15, textColor=TERRACOTTA, spaceAfter=6,
        ),
    }

    metadata = report.get("metadata") if isinstance(report.get("metadata"), dict) else {}
    generated = _text(metadata.get("generated", "")).strip()

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.72 * inch,
        rightMargin=0.72 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.78 * inch,
        title="SAGE Executive Decision Brief",
        author="SAGE",
        subject=_text(brief.get("problem", "SAGE research brief")),
    )

    problem = _flatten(brief.get("problem") or metadata.get("business_problem"), limit=200)
    market = _flatten(brief.get("market") or metadata.get("target_market"), limit=140)
    decision = _flatten(brief.get("decision") or metadata.get("business_decision"), limit=200)

    story = []

    # ---- Cover / framing ----
    story.append(Paragraph("SAGE", ParagraphStyle(
        "SAGEBrand", parent=stylesheet["Title"], fontName=bold_font,
        fontSize=10.5, leading=13, textColor=BRASS, alignment=TA_LEFT, spaceAfter=6,
    )))
    story.append(Paragraph("Executive Decision Brief", ParagraphStyle(
        "SAGETitle", parent=stylesheet["Title"], fontName="Times-Bold",
        fontSize=25, leading=30, textColor=INK, alignment=TA_LEFT, spaceAfter=8,
    )))
    if problem:
        story.append(Paragraph(escape(problem), ParagraphStyle(
            "SAGEProblem", parent=stylesheet["Title"], fontName="Times-Bold",
            fontSize=15.5, leading=20, textColor=INK_SOFT, alignment=TA_LEFT, spaceAfter=8,
        )))
    meta_bits = []
    if market:
        meta_bits.append(f"<b>Target market</b> &nbsp;{escape(market)}")
    if decision:
        meta_bits.append(f"<b>Decision</b> &nbsp;{escape(decision)}")
    if meta_bits:
        story.append(Paragraph(" &nbsp;&nbsp;\u2022&nbsp;&nbsp; ".join(meta_bits), styles["Meta"]))
    story.append(_rule(space_before=10, space_after=14))

    takeaway = _flatten(report.get("decision_takeaway"), limit=520)
    if takeaway:
        story.append(_kicker("Executive conclusion", styles))
        quote_table = Table(
            [[_paragraph(takeaway, styles["Quote"])]],
            colWidths=[CONTENT_WIDTH],
        )
        quote_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PALE),
            ("LINEBEFORE", (0, 0), (0, -1), 2.4, BRASS),
            ("LEFTPADDING", (0, 0), (-1, -1), 16),
            ("RIGHTPADDING", (0, 0), (-1, -1), 16),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ]))
        story.append(quote_table)
        story.append(Spacer(1, 14))

    summary = report.get("executive_summary")
    if isinstance(summary, str) and summary.strip():
        story.append(_kicker("Executive summary", styles))
        story.append(_paragraph(summary.strip(), styles["Body"]))
        story.append(Spacer(1, 6))
    elif not _empty(summary):
        story.append(_kicker("Executive summary", styles))
        story.append(_paragraph(_flatten(summary, limit=700), styles["Body"]))
        story.append(Spacer(1, 6))

    stats = [
        ("Key findings", len(_as_list(report.get("key_findings")))),
        ("Opportunities", len(_as_list(report.get("opportunities")))),
        ("Risks", len(_as_list(report.get("risks")))),
        ("Sources", len(_as_list(intelligence.get("sources")))),
    ]
    stats = [(label, count) for label, count in stats if count]
    if stats:
        story.append(Spacer(1, 4))
        cells = [[Paragraph(str(count), styles["StatValue"]) for _, count in stats]]
        labels_row = [[Paragraph(label.upper(), styles["StatLabel"]) for label, _ in stats]]
        stat_table = Table(cells + labels_row, colWidths=[CONTENT_WIDTH / len(stats)] * len(stats))
        stat_table.setStyle(TableStyle([
            ("LINEABOVE", (0, 0), (-1, 0), 1.2, RULE),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 4),
        ]))
        story.append(stat_table)

    # ---- Key facts & figures ----
    findings = _top(report.get("key_findings"), 4)
    if findings:
        story.append(CondPageBreak(1.6 * inch))
        story.append(Paragraph("Key Facts &amp; Figures", styles["Section"]))
        story.append(_rule())
        for item in findings:
            story.append(_finding_block(item, styles))

    chart_data = derive_market_chart_data(intelligence) or derive_single_period_chart_data(intelligence)
    drawing = _mini_chart(chart_data)
    if drawing is not None:
        story.append(Paragraph(escape(_text(chart_data.get("title", "Reported figures"))), styles["ItemTitle"]))
        story.append(drawing)
        story.append(Spacer(1, 6))

    # ---- Market / customer / competitive signals (condensed) ----
    story.append(PageBreak())
    story.append(Paragraph("Market, Customer &amp; Competitive Signals", styles["Section"]))
    story.append(_rule())

    market_overview = report.get("market_overview")
    if isinstance(market_overview, dict):
        highlights = []
        for key in ("market_characteristics", "characteristics", "demand_patterns", "demand", "important_developments", "developments"):
            highlights.extend(_as_list(market_overview.get(key)))
    else:
        highlights = _as_list(market_overview)
    highlights = highlights[:4]
    if highlights:
        story.append(_kicker("Market", styles))
        for item in highlights:
            story.append(_paragraph(f"\u2022 {_flatten(item, limit=220)}", styles["Body"]))

    segments = report.get("customer_insights")
    segments = _as_list(segments.get("segments") if isinstance(segments, dict) else segments)[:2]
    if segments:
        story.append(_kicker("Customers", styles))
        for item in segments:
            name = _flatten(_lookup(item, ("segment", "name", "title", "group")) or item, limit=60)
            desc = _flatten(_lookup(item, ("description", "profile", "behavior", "need")) if isinstance(item, dict) else None, limit=180)
            markup = f"<b>{escape(name)}</b> \u2014 {escape(desc)}" if desc else f"<b>{escape(name)}</b>"
            story.append(_rich(markup, styles["Body"]))

    competitors = report.get("competitive_landscape")
    competitors = _as_list(competitors.get("competitors") if isinstance(competitors, dict) else competitors)[:2]
    if competitors:
        story.append(_kicker("Competition", styles))
        for item in competitors:
            name = _flatten(_lookup(item, ("competitor", "name", "company", "brand")) or item, limit=60)
            desc = _flatten(_lookup(item, ("differentiation", "positioning", "strengths", "notes", "description")) if isinstance(item, dict) else None, limit=180)
            markup = f"<b>{escape(name)}</b> \u2014 {escape(desc)}" if desc else f"<b>{escape(name)}</b>"
            story.append(_rich(markup, styles["Body"]))

    trends = _top(report.get("market_trends"), 2)
    if trends:
        story.append(_kicker("Trends", styles))
        for item in trends:
            story.append(_paragraph(f"\u2022 {_flatten(item, limit=200)}", styles["Body"]))

    # ---- Strategic implications ----
    insights = _top(report.get("strategic_insights"), 3)
    if insights:
        story.append(PageBreak())
        story.append(Paragraph("Strategic Implications", styles["Section"]))
        story.append(_rule())
        for item in insights:
            main = _flatten(_lookup(item, ("implication", "insight", "strategic_insight", "title", "statement")) or item, limit=260)
            meaning = _flatten(_lookup(item, ("business_meaning", "why_it_matters", "so_what")), limit=200)
            story.append(_paragraph(main, styles["LeadItem"]))
            if meaning:
                story.append(_paragraph(meaning, styles["Meta"]))
            story.append(Spacer(1, 8))

    # ---- Opportunities & risks, side by side ----
    opportunities = _top(report.get("opportunities"), 3)
    risks = _top(report.get("risks"), 3)
    if opportunities or risks:
        story.append(CondPageBreak(2.2 * inch))
        story.append(Paragraph("Opportunities &amp; Risks", styles["Section"]))
        story.append(_rule())
        opp_flow = [Paragraph("Opportunities", styles["ColHead"])]
        for item in opportunities:
            opp_flow.extend(_signal_block(item, styles))
        risk_flow = [Paragraph("Risks", styles["ColHeadRisk"])]
        for item in risks:
            risk_flow.extend(_signal_block(item, styles))
        two_col = Table([[opp_flow, risk_flow]], colWidths=[CONTENT_WIDTH / 2 - 10, CONTENT_WIDTH / 2 - 10])
        two_col.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 20),
            ("LEFTPADDING", (1, 0), (1, 0), 20),
            ("LINEBEFORE", (1, 0), (1, 0), 0.7, RULE),
        ]))
        story.append(two_col)
        story.append(Spacer(1, 10))

    # ---- Recommended actions ----
    actions = _top(report.get("recommended_actions"), 4)
    if actions:
        story.append(CondPageBreak(2 * inch))
        story.append(Paragraph("Recommended Actions", styles["Section"]))
        story.append(_rule())
        for index, item in enumerate(actions, 1):
            story.append(_action_block(item, index, styles))

    # ---- Validation ----
    validation_items = (
        _top(validation.get("validation_questions"), 2)
        + _top(validation.get("evidence_gaps"), 2)
    )
    if validation_items:
        story.append(CondPageBreak(1.6 * inch))
        story.append(Paragraph("What Still Needs Validation", styles["Section"]))
        story.append(_rule())
        for item in validation_items:
            story.append(_paragraph(f"\u2022 {_flatten(item, limit=220)}", styles["Body"]))
        story.append(Spacer(1, 8))
        story.append(_paragraph(
            "The full evidence ledger, source register and research trail behind this brief "
            "are available in the SAGE workspace and the JSON export.",
            styles["Meta"],
        ))

    if len(story) <= 4:
        story.append(_paragraph("No report sections contained exportable content.", styles["Body"]))

    def draw_page(canvas, doc):
        _draw_page(canvas, doc, regular_font, bold_font, generated)

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return buffer.getvalue()
