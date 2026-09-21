from openai import OpenAI
from datetime import datetime
import json
import re
import time


# ============================================================
# SAGE V3.3
# MULTI-STAGE BUSINESS INTELLIGENCE ENGINE
# ============================================================

client = OpenAI(timeout=300.0)

# ============================================================
# REAL-TIME TELEMETRY
# ============================================================

def emit_event(event_name, message):
    """Emit a machine-readable progress event for the Streamlit UI."""
    safe_message = str(message).replace("\r", " ").replace("\n", " ").strip()
    print(f"SAGE_EVENT|{event_name}|{safe_message}", flush=True)



# ============================================================
# HELPERS
# ============================================================

def clean_json(text):
    """Clean common formatting issues from model JSON output."""

    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def run_stage(stage_name, prompt, use_web=False):
    """Run one SAGE research stage."""

    stage_labels = {
        "STAGE 1 - RESEARCH DESIGN": "Research Design",
        "STAGE 2 - WEB RESEARCH": "Web Research",
        "STAGE 3 - BUSINESS INTELLIGENCE ANALYSIS": "Business Intelligence",
        "STAGE 4 - STRATEGIC SYNTHESIS": "Strategic Synthesis",
    }

    emit_event("STAGE_STARTED", stage_labels.get(stage_name, stage_name))

    print("\n" + "=" * 70)
    print(stage_name)
    print("=" * 70)

    tools = []

    if use_web:
        tools.append({
            "type": "web_search",
            "search_context_size": "medium"
        })

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            tools=tools,
            input=prompt
        )

        output = response.output_text.strip()

        print(f"\n[OK] {stage_name} completed.")

        return output

    except Exception as error:

        emit_event("ERROR", f"{stage_name} failed")

        print(
            f"\n[ERROR] {stage_name} failed: {error}"
        )

        raise


def parse_json(output, stage_name):
    """Parse JSON and attempt one recovery if required."""

    cleaned = clean_json(output)

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:

        print(
            f"\n[WARNING] {stage_name} returned invalid JSON."
        )

        recovery_prompt = f"""
Convert the following response into valid JSON.

Rules:

1. Return ONLY valid JSON.
2. Do not use markdown.
3. Do not add explanations.
4. Preserve all substantive information.
5. Do not invent information.
6. Do not remove important fields.

Response:

{output}
"""

        recovery = client.responses.create(
            model="gpt-5.6-luna",
            input=recovery_prompt
        )

        recovered = clean_json(
            recovery.output_text
        )

        try:

            return json.loads(recovered)

        except json.JSONDecodeError:

            raise RuntimeError(
                f"{stage_name} could not be converted into valid JSON."
            )


def safe_list(value):
    """Always return a list."""

    if isinstance(value, list):
        return value

    if value is None:
        return []

    return [value]


def safe_dict(value):
    """Always return a dictionary."""

    if isinstance(value, dict):
        return value

    return {}


# ============================================================
# USER INPUT
# ============================================================

business_problem = input(
    "What business problem should SAGE research?\n\n> "
)

target_market = input(
    "\nWhich country or market should SAGE focus on?\n\n> "
)

business_decision = input(
    "\nWhat business decision should this research help with?\n\n> "
)


start_time = datetime.now()


print("\n")
print("=" * 70)
print("                    SAGE V3.2")
print("       AUTONOMOUS BUSINESS INTELLIGENCE ENGINE")
print("=" * 70)

print("\nSAGE is building a research strategy...")
print("The research will happen in four stages.\n")


# ============================================================
# STAGE 1
# RESEARCH DESIGN
# ============================================================

planning_prompt = f"""
You are SAGE, an autonomous business research strategist.

Your job is to design a focused research plan before research begins.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

BUSINESS DECISION:
{business_decision}

Create a practical research blueprint.

Identify:

1. The central business question.
2. 5-7 specific research questions.
3. Customer information that must be investigated.
4. Competitor information that must be investigated.
5. Market information that must be investigated.
6. Trends that may affect the decision.
7. Risks and constraints.
8. Evidence that would be required to support conclusions.

Avoid generic questions.

The research must ultimately help answer the stated business decision.

Return ONLY valid JSON.

Required structure:

{{
    "research_objective": "",
    "research_questions": [],
    "customer_questions": [],
    "competitor_questions": [],
    "market_questions": [],
    "trend_questions": [],
    "risk_questions": [],
    "evidence_requirements": []
}}
"""


research_plan_raw = run_stage(
    "STAGE 1 - RESEARCH DESIGN",
    planning_prompt,
    use_web=False
)

research_plan = parse_json(
    research_plan_raw,
    "Research Design"
)

research_questions = safe_list(research_plan.get("research_questions"))
if research_questions:
    emit_event(
        "RESEARCH_QUESTIONS",
        f"{len(research_questions)} research questions identified"
    )


# ============================================================
# STAGE 2
# EVIDENCE COLLECTION
# ============================================================

research_prompt = f"""
You are SAGE, a professional business research analyst.

Conduct evidence-based web research for the business problem below.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

BUSINESS DECISION:
{business_decision}

RESEARCH PLAN:
{json.dumps(research_plan, indent=2)}

Collect evidence relevant to the decision.

Investigate:

MARKET
- Market structure
- Demand patterns
- Market growth
- Market economics
- Important developments

CUSTOMERS
- Important customer segments
- Needs
- Pain points
- Purchase drivers
- Behavioral patterns
- Price sensitivity where evidence exists

COMPETITORS
- Major competitors
- Direct and indirect alternatives
- Positioning
- Value proposition
- Strengths
- Gaps
- Pricing signals where available

TRENDS
- Important current trends
- Emerging changes
- Technology
- Consumer behavior
- Regulatory or structural developments

RISKS
- Competitive risks
- Economic risks
- Operational risks
- Regulatory risks
- Customer risks

OPPORTUNITIES
- Evidence-backed market opportunities

SOURCE PRIORITY:

1. Government
2. Regulatory organizations
3. Official company sources
4. Industry associations
5. Academic research
6. Reputable research organizations
7. Reputable business publications

IMPORTANT:

- Prefer recent information.
- Cross-check important claims.
- Do not invent statistics.
- Do not invent sources.
- Clearly mark uncertain information.
- Keep the target market in focus.
- Separate evidence from interpretation.
- Include source information for important claims.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "market_evidence": [
        {{
            "finding": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "customer_evidence": [
        {{
            "segment": "",
            "finding": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "competitor_evidence": [
        {{
            "competitor": "",
            "type": "",
            "finding": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "trend_evidence": [
        {{
            "trend": "",
            "finding": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "opportunity_evidence": [
        {{
            "opportunity": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "risk_evidence": [
        {{
            "risk": "",
            "evidence": "",
            "evidence_strength": ""
        }}
    ],

    "important_statistics": [
        {{
            "statistic": "",
            "context": "",
            "source": ""
        }}
    ],

    "evidence_gaps": [],

    "sources": [
        {{
            "source": "",
            "organization": "",
            "url": "",
            "information_supported": "",
            "source_quality": ""
        }}
    ]
}}
"""


research_raw = run_stage(
    "STAGE 2 - WEB RESEARCH",
    research_prompt,
    use_web=True
)

research_data = parse_json(
    research_raw,
    "Web Research"
)

research_sources = safe_list(research_data.get("sources"))
for source_item in research_sources[:8]:
    if isinstance(source_item, dict):
        source_name = (
            source_item.get("source")
            or source_item.get("organization")
            or source_item.get("url")
        )
    else:
        source_name = source_item

    if source_name:
        emit_event("SOURCE_FOUND", str(source_name))

emit_event("EVIDENCE_COMPLETE", "Evidence collection completed")


# ============================================================
# STAGE 3
# BUSINESS INTELLIGENCE ANALYSIS
# ============================================================

analysis_prompt = f"""
You are SAGE, a senior business intelligence analyst.

Analyze the evidence collected by SAGE.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

BUSINESS DECISION:
{business_decision}

RESEARCH EVIDENCE:
{json.dumps(research_data, indent=2)}

Your task is NOT to repeat the evidence.

Transform the evidence into concise business analysis suitable for an executive dashboard.

The underlying research can be detailed, but the output fields shown in the main dashboard must be easy to scan. Keep supporting detail in the research_evidence data rather than expanding dashboard-facing text.

Separate:

EVIDENCE
What is supported by research.

ANALYSIS
What the evidence means.

IMPLICATION
Why the finding matters for the business decision.

Do not create strategic recommendations yet.

Create:

1. Market analysis
2. Customer segments
3. Competitive analysis
4. Trend analysis
5. Opportunities
6. Risks
7. Evidence assessment

Avoid repeating the same idea across sections.

Each finding should have a clear reason for being included.

Aim for approximately:

- 4-5 market findings
- 3-5 customer segments
- 4-6 competitor findings
- 4-6 trends
- 3-5 opportunities
- 3-5 risks

MARKET ANALYSIS DISPLAY RULES:
The market overview is a dashboard section, not a long-form report.

For each market finding:
- "finding": one strong, specific headline or sentence, ideally 8-14 words.
- "evidence": 1 concise sentence containing the most relevant supporting fact, statistic, or observed evidence. Maximum about 30 words.
- "implication": 1 concise sentence explaining why it matters to the business decision. Maximum about 25 words.
- Do not use multiple paragraphs.
- Do not repeat the same point across findings.
- Prefer concrete market signals, demand patterns, structural characteristics, or developments.
- If a statistic is available, prioritize the statistic over generic explanation.
- Keep the full underlying evidence in the research evidence section; the market_analysis output should be executive-friendly.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "market_analysis": [
        {{
            "finding": "",
            "evidence": "",
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "customer_analysis": [
        {{
            "segment": "",
            "needs": [],
            "pain_points": [],
            "purchase_drivers": [],
            "behavior": "",
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "competitive_analysis": [
        {{
            "competitor": "",
            "type": "",
            "positioning": "",
            "strengths": [],
            "gaps": [],
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "trend_analysis": [
        {{
            "trend": "",
            "evidence": "",
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "opportunity_analysis": [
        {{
            "opportunity": "",
            "customer_problem": "",
            "market_reason": "",
            "evidence": "",
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "risk_analysis": [
        {{
            "risk": "",
            "potential_impact": "",
            "evidence": "",
            "implication": "",
            "evidence_strength": ""
        }}
    ],

    "evidence_assessment": {{
        "strong_evidence": [],
        "moderate_evidence": [],
        "weak_evidence": [],
        "contradictions": [],
        "important_gaps": []
    }}
}}
"""


analysis_raw = run_stage(
    "STAGE 3 - BUSINESS INTELLIGENCE ANALYSIS",
    analysis_prompt,
    use_web=False
)

analysis_data = parse_json(
    analysis_raw,
    "Business Intelligence Analysis"
)

emit_event(
    "ANALYSIS_COMPLETE",
    "Business intelligence analysis completed"
)


# ============================================================
# BUILD COMPACT STRATEGIC INPUT
# ============================================================

compact_strategy_input = {
    "market_analysis": safe_list(
        analysis_data.get("market_analysis")
    ),

    "customer_analysis": safe_list(
        analysis_data.get("customer_analysis")
    ),

    "competitive_analysis": safe_list(
        analysis_data.get("competitive_analysis")
    ),

    "trend_analysis": safe_list(
        analysis_data.get("trend_analysis")
    ),

    "opportunity_analysis": safe_list(
        analysis_data.get("opportunity_analysis")
    ),

    "risk_analysis": safe_list(
        analysis_data.get("risk_analysis")
    ),

    "evidence_assessment": safe_dict(
        analysis_data.get("evidence_assessment")
    )
}


# ============================================================
# STAGE 4
# STRATEGIC SYNTHESIS
# ============================================================

strategy_prompt = f"""
You are SAGE, a senior strategy consultant.

Create a concise decision-ready strategy based on the business
intelligence analysis below.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

BUSINESS DECISION:
{business_decision}

BUSINESS INTELLIGENCE:

{json.dumps(compact_strategy_input, indent=2)}

IMPORTANT:

Do NOT repeat the market findings word-for-word.

Do NOT create another generic list of "insights".

Instead:

1. Select the most decision-relevant findings.
2. Explain their strategic meaning.
3. Identify the highest-value opportunities.
4. Identify the most important risks.
5. Create specific recommended actions.
6. Link every recommendation to one or more findings.
7. Identify what should be validated before major investment.

The final strategy should answer:

"Given the evidence, what should the business pay attention to
and what should it do next?"

Keep the strategy compact and non-repetitive.

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "executive_summary": "",

    "key_findings": [
        {{
            "finding": "",
            "why_it_matters": "",
            "evidence_strength": ""
        }}
    ],

    "strategic_implications": [
        {{
            "implication": "",
            "based_on": "",
            "business_meaning": ""
        }}
    ],

    "priority_opportunities": [
        {{
            "opportunity": "",
            "why_it_matters": "",
            "supporting_finding": "",
            "execution_considerations": ""
        }}
    ],

    "priority_risks": [
        {{
            "risk": "",
            "why_it_matters": "",
            "mitigation": ""
        }}
    ],

    "recommended_actions": [
        {{
            "priority": "",
            "action": "",
            "based_on_finding": "",
            "reason": "",
            "expected_impact": "",
            "implementation_note": ""
        }}
    ],

    "decision_takeaway": "",

    "what_to_validate_next": [],

    "research_confidence": "",

    "research_limitations": []
}}
"""


strategy_raw = run_stage(
    "STAGE 4 - STRATEGIC SYNTHESIS",
    strategy_prompt,
    use_web=False
)

strategy_data = parse_json(
    strategy_raw,
    "Strategic Synthesis"
)

emit_event(
    "SYNTHESIS_COMPLETE",
    "Strategic synthesis completed"
)


# ============================================================
# NORMALIZE DATA
# ============================================================

market_analysis = safe_list(
    analysis_data.get("market_analysis")
)

customer_analysis = safe_list(
    analysis_data.get("customer_analysis")
)

competitive_analysis = safe_list(
    analysis_data.get("competitive_analysis")
)

trend_analysis = safe_list(
    analysis_data.get("trend_analysis")
)

opportunity_analysis = safe_list(
    analysis_data.get("opportunity_analysis")
)

risk_analysis = safe_list(
    analysis_data.get("risk_analysis")
)

evidence_assessment = safe_dict(
    analysis_data.get("evidence_assessment")
)


key_findings = safe_list(
    strategy_data.get("key_findings")
)

strategic_implications = safe_list(
    strategy_data.get("strategic_implications")
)

priority_opportunities = safe_list(
    strategy_data.get("priority_opportunities")
)

priority_risks = safe_list(
    strategy_data.get("priority_risks")
)

recommended_actions = safe_list(
    strategy_data.get("recommended_actions")
)


# ============================================================
# BACKWARD-COMPATIBLE DASHBOARD STRUCTURE
# ============================================================

final_output = {

    "metadata": {
        "version": "SAGE V3.3",
        "generated": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "duration_seconds": int(
            (datetime.now() - start_time).total_seconds()
        ),
        "business_problem": business_problem,
        "target_market": target_market,
        "business_decision": business_decision
    },


    # --------------------------------------------------------
    # EXECUTIVE
    # --------------------------------------------------------

    "executive_summary": strategy_data.get(
        "executive_summary",
        ""
    ),


    "key_findings": key_findings,


    # --------------------------------------------------------
    # MARKET
    # --------------------------------------------------------

    "market_overview": {

        "market_characteristics": market_analysis,

        "demand_patterns": [
            {
                "pattern": item.get(
                    "finding",
                    ""
                ),
                "evidence": item.get(
                    "evidence",
                    ""
                ),
                "evidence_strength": item.get(
                    "evidence_strength",
                    ""
                )
            }

            for item in market_analysis
        ],

        "important_developments": [
            {
                "development": item.get(
                    "implication",
                    ""
                ),
                "evidence": item.get(
                    "evidence",
                    ""
                ),
                "evidence_strength": item.get(
                    "evidence_strength",
                    ""
                )
            }

            for item in market_analysis
        ]
    },


    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    "customer_insights": customer_analysis,


    # --------------------------------------------------------
    # COMPETITION
    # --------------------------------------------------------

    "competitive_landscape": competitive_analysis,


    # --------------------------------------------------------
    # TRENDS
    # --------------------------------------------------------

    "market_trends": trend_analysis,


    # --------------------------------------------------------
    # OPPORTUNITIES
    # --------------------------------------------------------

    "opportunities": priority_opportunities,


    # --------------------------------------------------------
    # RISKS
    # --------------------------------------------------------

    "risks": priority_risks,


    # --------------------------------------------------------
    # STRATEGIC THINKING
    # --------------------------------------------------------

    "strategic_insights": strategic_implications,


    # --------------------------------------------------------
    # ACTION PLAN
    # --------------------------------------------------------

    "recommended_actions": recommended_actions,


    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    "decision_takeaway": strategy_data.get(
        "decision_takeaway",
        ""
    ),


    # --------------------------------------------------------
    # EVIDENCE QUALITY
    # --------------------------------------------------------

    "evidence_quality": {

        "strong_findings": safe_list(
            evidence_assessment.get(
                "strong_evidence"
            )
        ),

        "reasonable_findings": safe_list(
            evidence_assessment.get(
                "moderate_evidence"
            )
        ),

        "uncertain_findings": safe_list(
            evidence_assessment.get(
                "weak_evidence"
            )
        ),

        "research_limitations": safe_list(
            strategy_data.get(
                "research_limitations"
            )
        )
    },


    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    "sources": safe_list(
        research_data.get(
            "sources"
        )
    ),


    # --------------------------------------------------------
    # FULL V3.1 DATA
    # --------------------------------------------------------

    "research_plan": research_plan,

    "research_evidence": research_data,

    "business_intelligence": analysis_data,

    "strategic_synthesis": strategy_data
}


# ============================================================
# SAVE
# ============================================================

with open(
    "sage_research_data.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_output,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# COMPLETE
# ============================================================

duration = int(
    (datetime.now() - start_time).total_seconds()
)

print("\n")
print("=" * 70)
print("              SAGE V3.3 RESEARCH COMPLETE")
print("=" * 70)

print(f"\nResearch duration: {duration} seconds")

print("\n[OK] Research design")
print("[OK] Web evidence collection")
print("[OK] Business intelligence analysis")
print("[OK] Strategic synthesis")

print("\nStructured intelligence saved as:")
print("sage_research_data.json")

print("\nSAGE V3.3 is ready.")