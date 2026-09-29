"""Pure normalization helpers for SAGE's evidence and source data."""

import math
import re


VALUE_PATTERN = re.compile(
    r"(?P<value>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)\s*"
    r"(?P<unit>crores?|lakhs?|millions?|billions?|thousands?|"
    r"%|percent|per cent|users?|customers?|patients?|transactions?|"
    r"outlets?|stores?|brands?|categories?|facilities|units?)"
    r"(?=\s|$|[.,;])",
    re.IGNORECASE,
)
PERIOD_PATTERN = re.compile(
    r"\bFY\s*\d{4}(?:\s*[-–/]\s*\d{2,4})?\b|\b(?:19|20)\d{2}\b",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
CURRENCY_PATTERN = re.compile(
    r"(?<!\w)(INR|USD|EUR|GBP|Rs\.?|\$|€|£)\s*$", re.IGNORECASE
)


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _key(value):
    return re.sub(r"[^a-z0-9]+", "", _text(value).casefold())


def _first_text(item, keys):
    for key in keys:
        text = _text(item.get(key))
        if text:
            return text
    return ""


def _normalized_source(item, index):
    if isinstance(item, dict):
        title = _first_text(item, ("title", "name", "source", "site", "publication"))
        organization = _first_text(item, ("organization", "publisher", "author"))
        url = _first_text(item, ("url", "link", "href", "source_url", "uri"))
        quality = _first_text(item, ("source_quality", "quality"))
        supported = _first_text(item, ("information_supported", "supports", "description"))
    else:
        title, organization, url, quality, supported = _text(item), "", "", "", ""

    if title.lower().startswith(("http://", "https://")) and not url:
        url, title = title, ""
    source_id = f"source-{index:04d}"
    return {
        "id": source_id,
        "title": title,
        "organization": organization,
        "url": url,
        "source_quality": quality,
        "information_supported": supported,
    }


def _source_index(sources):
    url_index, name_index = {}, {}
    for source in sources:
        if source["url"]:
            url_index.setdefault(_key(source["url"].rstrip("/")), []).append(source["id"])
        for label in (source["title"], source["organization"]):
            if label:
                name_index.setdefault(_key(label), []).append(source["id"])
    return url_index, name_index


def _reference_values(item):
    refs = []
    for key in ("source_ids", "source_urls", "source_url", "url", "link", "source", "sources", "citation", "citations"):
        value = item.get(key)
        for ref in _as_list(value):
            if isinstance(ref, dict):
                ref = _first_text(ref, ("url", "link", "source_url", "source", "title", "name"))
            text = _text(ref)
            if text:
                refs.append(text)
    return refs


def _matched_source_ids(item, url_index, name_index, known_ids):
    matched = set()
    for reference in _reference_values(item):
        if reference in known_ids:
            matched.add(reference)
            continue
        urls = [url.rstrip(".,;)") for url in URL_PATTERN.findall(reference)]
        if urls:
            for url in urls:
                ids = url_index.get(_key(url), [])
                if len(ids) == 1:
                    matched.add(ids[0])
            continue
        ids = name_index.get(_key(reference), [])
        if len(ids) == 1:
            matched.add(ids[0])
    return sorted(matched)


def _comparable_series(statistic, source_ids):
    values = list(VALUE_PATTERN.finditer(statistic))
    periods = list(PERIOD_PATTERN.finditer(statistic))
    if len(values) < 2 or len(values) != len(periods):
        return None

    units = [match.group("unit").casefold().rstrip("s") for match in values]
    if len(set(units)) != 1:
        return None
    try:
        numbers = [float(match.group("value").replace(",", "")) for match in values]
    except ValueError:
        return None
    if len(set(numbers)) < 2:
        return None

    currencies = []
    for match in values:
        currency = CURRENCY_PATTERN.search(statistic[max(0, match.start() - 12):match.start()])
        currencies.append(currency.group(1).casefold() if currency else "")
    if len(set(currencies)) != 1:
        return None

    observations = [
        {"period": period.group(0).replace(" ", ""), "value": number}
        for period, number in zip(periods, numbers)
    ]
    observations.sort(key=lambda observation: int(re.search(r"(?:19|20)\d{2}", observation["period"]).group(0)))
    return {
        "unit": values[0].group("unit"),
        "currency": currencies[0],
        "source_ids": source_ids,
        "observations": observations,
    }


def _explicit_comparison_series(item, source_ids):
    """Normalize only caller-supplied metric series with explicit periods and values."""
    raw_series = item.get("numeric_series")
    if not isinstance(raw_series, dict) and isinstance(item.get("statistic"), dict):
        raw_series = item["statistic"]
    if not isinstance(raw_series, dict):
        raw_series = item

    metric = _first_text(item, ("metric", "metric_name", "measure_name")) or _first_text(
        raw_series, ("metric", "metric_name", "measure_name")
    )
    observations = raw_series.get("observations")
    if not isinstance(observations, list) and "period" in raw_series and "value" in raw_series:
        observations = [raw_series]
    if not metric or not isinstance(observations, list) or not observations:
        return None

    normalized = []
    for observation in observations:
        if not isinstance(observation, dict):
            return None
        period = _first_text(observation, ("period",))
        value = observation.get("value")
        unit = (
            _first_text(observation, ("unit",))
            or _first_text(raw_series, ("unit",))
            or _first_text(item, ("unit",))
        )
        currency = (
            _first_text(observation, ("currency",))
            or _first_text(raw_series, ("currency",))
            or _first_text(item, ("currency",))
        )
        if (
            not period or not unit or isinstance(value, bool)
            or not isinstance(value, (int, float)) or not math.isfinite(value)
        ):
            return None
        normalized.append({"period": period, "value": value, "unit": unit, "currency": currency})

    units = {_key(observation["unit"]) for observation in normalized}
    currencies = {_key(observation["currency"]) for observation in normalized}
    if len(units) != 1 or len(currencies) != 1:
        return None

    return {
        "metric": metric,
        "unit": normalized[0]["unit"],
        "currency": normalized[0]["currency"],
        "source_ids": source_ids,
        "observations": [
            {"period": observation["period"], "value": observation["value"]}
            for observation in normalized
        ],
    }


def _explicit_numeric_measures(item, source_ids):
    """Accept only caller-supplied labeled numeric measures with an explicit shared unit."""
    measures = item.get("measures")
    if not isinstance(measures, list) or len(measures) < 2:
        return None
    normalized = []
    for measure in measures:
        if not isinstance(measure, dict):
            return None
        label = _first_text(measure, ("label", "name", "metric"))
        unit = _first_text(measure, ("unit",))
        value = measure.get("value")
        if not label or not unit or isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        normalized.append({"label": label, "value": value, "unit": unit})
    units = {_key(measure["unit"]) for measure in normalized}
    if len(units) != 1 or len({_key(measure["label"]) for measure in normalized}) != len(normalized):
        return None
    return {"unit": normalized[0]["unit"], "source_ids": source_ids, "observations": normalized}


def build_evidence_intelligence(research_evidence, business_intelligence, strategic_synthesis=None):
    """Normalize existing SAGE evidence without inventing links, scores, or values."""
    research_evidence = research_evidence if isinstance(research_evidence, dict) else {}
    business_intelligence = business_intelligence if isinstance(business_intelligence, dict) else {}
    strategic_synthesis = strategic_synthesis if isinstance(strategic_synthesis, dict) else {}

    sources = []
    source_keys = set()
    for raw_source in _as_list(research_evidence.get("sources")):
        normalized = _normalized_source(raw_source, len(sources) + 1)
        dedupe_key = _key(normalized["url"] or normalized["title"] or normalized["organization"])
        if dedupe_key and dedupe_key in source_keys:
            continue
        if dedupe_key:
            source_keys.add(dedupe_key)
        sources.append(normalized)

    url_index, name_index = _source_index(sources)
    known_ids = {source["id"] for source in sources}
    items = []

    def add_items(category, records, record_type):
        for raw_item in _as_list(records):
            if isinstance(raw_item, dict):
                item = raw_item
            elif isinstance(raw_item, str):
                item = {"evidence": raw_item}
            else:
                continue
            claim = _first_text(item, (
                "finding", "claim", "title", "trend", "segment", "competitor",
                "opportunity", "risk", "pattern", "development", "statistic",
            ))
            evidence = _first_text(item, (
                "evidence", "supporting_evidence", "information_supported", "description",
            ))
            statistic = _text(item.get("statistic")) if record_type == "statistic" else ""
            if statistic and not evidence:
                evidence = statistic
            context = _first_text(item, ("context", "implication", "why_it_matters"))
            source_ids = _matched_source_ids(item, url_index, name_index, known_ids)
            comparison_series = _explicit_comparison_series(item, source_ids)
            normalized_item = {
                "id": f"evidence-{len(items) + 1:04d}",
                "record_type": record_type,
                "category": category,
                "claim": claim,
                "evidence": evidence,
                "context": context,
                "evidence_strength": _first_text(item, (
                    "evidence_strength", "strength", "evidence_level",
                )) or None,
                "source_ids": source_ids,
                "numeric_series": _comparable_series(statistic, source_ids) if statistic else None,
                "comparison_numeric_series": comparison_series,
                "numeric_measures": _explicit_numeric_measures(item, source_ids),
                "explicit_metric": (
                    comparison_series["metric"] if comparison_series
                    else _first_text(item, ("metric", "metric_name", "measure_name"))
                ),
                "details": item,
            }
            items.append(normalized_item)

    for category in (
        "market_evidence", "customer_evidence", "competitor_evidence",
        "trend_evidence", "opportunity_evidence", "risk_evidence",
    ):
        add_items(category.removesuffix("_evidence"), research_evidence.get(category), "research_evidence")
    add_items("market", research_evidence.get("important_statistics"), "statistic")

    for category in (
        "market_characteristics", "demand_analysis", "development_analysis",
        "customer_analysis", "competitive_analysis", "trend_analysis",
        "opportunity_analysis", "risk_analysis",
    ):
        add_items(category, business_intelligence.get(category), "business_intelligence")

    assessment = business_intelligence.get("evidence_assessment")
    assessment = assessment if isinstance(assessment, dict) else {}
    limitations = strategic_synthesis.get("research_limitations", [])

    return {
        "schema_version": 1,
        "sources": sources,
        "items": items,
        "evidence_gaps": _as_list(research_evidence.get("evidence_gaps")),
        "research_limitations": _as_list(limitations),
        "quality_assessment": {
            "strong_evidence": _as_list(assessment.get("strong_evidence")),
            "moderate_evidence": _as_list(assessment.get("moderate_evidence")),
            "weak_evidence": _as_list(assessment.get("weak_evidence")),
        },
    }


def build_validation_intelligence(report):
    """Collect SAGE-supplied validation context without reclassifying research questions."""
    report = report if isinstance(report, dict) else {}
    synthesis = report.get("strategic_synthesis")
    synthesis = synthesis if isinstance(synthesis, dict) else {}
    research_plan = report.get("research_plan")
    research_plan = research_plan if isinstance(research_plan, dict) else {}
    evidence = report.get("evidence_intelligence")
    evidence = evidence if isinstance(evidence, dict) else {}

    validation_questions = report.get("what_to_validate_next")
    if not validation_questions or (
        isinstance(validation_questions, str) and not validation_questions.strip()
    ):
        validation_questions = synthesis.get("what_to_validate_next", [])

    research_evidence = report.get("research_evidence")
    research_evidence = research_evidence if isinstance(research_evidence, dict) else {}
    evidence_quality = report.get("evidence_quality")
    evidence_quality = evidence_quality if isinstance(evidence_quality, dict) else {}
    evidence_gaps = evidence.get("evidence_gaps") or research_evidence.get("evidence_gaps")
    limitations = (
        evidence.get("research_limitations")
        or synthesis.get("research_limitations")
        or evidence_quality.get("research_limitations")
    )

    plan_questions = {
        key: _as_list(research_plan.get(key))
        for key in (
            "research_questions", "customer_questions", "competitor_questions",
            "market_questions", "trend_questions", "risk_questions", "evidence_requirements",
        )
        if research_plan.get(key)
    }
    return {
        "validation_questions": _as_list(validation_questions),
        "evidence_gaps": _as_list(evidence_gaps),
        "assumptions": _as_list(synthesis.get("assumptions")),
        "unresolved_questions": _as_list(synthesis.get("unresolved_questions")),
        "research_limitations": _as_list(limitations),
        "research_plan_questions": plan_questions,
    }


def derive_market_chart_data(evidence_intelligence):
    """Return the existing chart payload from normalized, comparable evidence."""
    if not isinstance(evidence_intelligence, dict):
        return None
    for item in evidence_intelligence.get("items", []):
        if not isinstance(item, dict) or not isinstance(item.get("numeric_series"), dict):
            continue
        series = item["numeric_series"]
        observations = series.get("observations", [])
        if len(observations) < 2:
            continue
        prefix = f"{series['currency'].upper()} " if series.get("currency") else ""
        return {
            "title": "Reported figures over time",
            "labels": [observation["period"] for observation in observations],
            "values": [observation["value"] for observation in observations],
            "value_prefix": prefix,
            "value_suffix": f" {series['unit']}",
        }
    return None


def derive_single_period_chart_data(evidence_intelligence):
    """Find explicitly labeled measures suitable for a same-unit categorical chart."""
    if not isinstance(evidence_intelligence, dict):
        return None
    for item in evidence_intelligence.get("items", []):
        if not isinstance(item, dict) or not isinstance(item.get("numeric_measures"), dict):
            continue
        measures = item["numeric_measures"]
        observations = measures.get("observations", [])
        if len(observations) >= 2:
            return {
                "title": to_text(item.get("claim")) or "Reported measures",
                "labels": [observation["label"] for observation in observations],
                "values": [observation["value"] for observation in observations],
                "value_suffix": f" {measures['unit']}",
            }
    return None


def derive_comparison_chart_data(evidence_a, evidence_b):
    """Compare only explicit, same-name metrics with identical units and periods."""
    if not isinstance(evidence_a, dict) or not isinstance(evidence_b, dict):
        return None

    def metric_map(evidence):
        result = {}
        invalid = set()
        for item in evidence.get("items", []):
            if not isinstance(item, dict) or not item.get("explicit_metric"):
                continue
            series = item.get("comparison_numeric_series")
            if not isinstance(series, dict) or not series.get("observations"):
                continue
            key = _key(item["explicit_metric"])
            if not key or key in invalid:
                continue
            existing = result.get(key)
            if existing is None:
                copied_series = dict(series)
                copied_series["observations"] = list(series["observations"])
                result[key] = {"item": item, "series": copied_series}
                continue
            current = existing["series"]
            if (
                _key(current.get("unit")) != _key(series.get("unit"))
                or _key(current.get("currency")) != _key(series.get("currency"))
            ):
                invalid.add(key)
                result.pop(key, None)
                continue
            by_period = {observation["period"]: observation["value"] for observation in current["observations"]}
            for observation in series["observations"]:
                period = observation["period"]
                if period in by_period and by_period[period] != observation["value"]:
                    invalid.add(key)
                    result.pop(key, None)
                    break
                if period not in by_period:
                    current["observations"].append(observation)
                    by_period[period] = observation["value"]
        return {
            key: value for key, value in result.items()
            if key not in invalid and len(value["series"].get("observations", [])) >= 2
        }

    a_metrics, b_metrics = metric_map(evidence_a), metric_map(evidence_b)
    for key in a_metrics.keys() & b_metrics.keys():
        item_a, series_a = a_metrics[key]["item"], a_metrics[key]["series"]
        item_b, series_b = b_metrics[key]["item"], b_metrics[key]["series"]
        unit_a, unit_b = _key(series_a.get("unit")), _key(series_b.get("unit"))
        currency_a, currency_b = _key(series_a.get("currency")), _key(series_b.get("currency"))
        obs_a, obs_b = series_a["observations"], series_b["observations"]
        periods_a = [observation["period"] for observation in obs_a]
        periods_b = [observation["period"] for observation in obs_b]
        if unit_a != unit_b or currency_a != currency_b or periods_a != periods_b:
            continue
        return {
            "title": to_text(item_a["explicit_metric"]),
            "labels": periods_a,
            "run_a_values": [observation["value"] for observation in obs_a],
            "run_b_values": [observation["value"] for observation in obs_b],
            "unit": series_a["unit"],
            "currency": series_a.get("currency", ""),
        }
    return None


def to_text(value):
    return value.strip() if isinstance(value, str) else ""
