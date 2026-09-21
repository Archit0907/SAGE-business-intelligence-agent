from openai import OpenAI
from datetime import datetime
import json

# ============================================================
# SAGE V2 - STRUCTURED BUSINESS RESEARCH ENGINE
# ============================================================

client = OpenAI(timeout=120.0)


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


print("\n" + "=" * 70)
print("              SAGE V2 RESEARCH STARTED")
print("=" * 70)

print("\nSAGE is researching the problem...")
print("Please wait...\n")


# ============================================================
# RESEARCH PROMPT
# ============================================================

research_prompt = f"""
You are SAGE, an AI-powered business research agent.

Your job is to research a business problem using reliable and
recent web information and convert the evidence into structured
business intelligence.

============================================================
BUSINESS INPUT
============================================================

Business Problem:
{business_problem}

Target Market:
{target_market}

Business Decision:
{business_decision}

============================================================
RESEARCH REQUIREMENTS
============================================================

Research the business problem deeply.

Do NOT automatically accept the premise of the question.

Identify:
- important facts
- market conditions
- customer behavior
- competitors
- substitutes
- trends
- opportunities
- risks
- uncertainties
- strategic implications

Prefer:
- government sources
- official company sources
- industry reports
- academic research
- reputable business publications

Cross-check important claims whenever possible.

Do not invent statistics or sources.

============================================================
STRUCTURED OUTPUT
============================================================

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
  "executive_summary": "",

  "key_findings": [
    ""
  ],

  "market_overview": {{
    "market_characteristics": [],
    "demand_patterns": [],
    "important_developments": []
  }},

  "customer_insights": [
    {{
      "segment": "",
      "needs": [],
      "purchase_drivers": [],
      "pain_points": [],
      "price_sensitivity": "",
      "evidence": []
    }}
  ],

  "competitive_landscape": [
    {{
      "competitor": "",
      "type": "",
      "value_proposition": "",
      "strengths": [],
      "gaps": [],
      "pricing": "",
      "evidence": []
    }}
  ],

  "market_trends": [
    {{
      "trend": "",
      "evidence": "",
      "business_implication": ""
    }}
  ],

  "opportunities": [
    {{
      "opportunity": "",
      "why_it_matters": "",
      "evidence": ""
    }}
  ],

  "risks": [
    {{
      "risk": "",
      "why_it_matters": "",
      "evidence": ""
    }}
  ],

  "evidence_quality": {{
    "strong_findings": [],
    "reasonable_findings": [],
    "uncertain_findings": [],
    "research_limitations": []
  }},

  "strategic_insights": [
    ""
  ],

  "recommended_actions": [
    {{
      "priority": "",
      "action": "",
      "reason": "",
      "expected_impact": "",
      "implementation_note": ""
    }}
  ],

  "decision_takeaway": "",

  "sources": [
    {{
      "source": "",
      "organization": "",
      "information_supported": ""
    }}
  ]
}}

============================================================
QUALITY RULES
============================================================

1. Every important factual claim must be supported by evidence.

2. Clearly distinguish facts from analysis.

3. If evidence is weak or unavailable, say so.

4. Do not present assumptions as facts.

5. Recommendations must logically follow from the evidence.

6. Respect the specified target market.

7. The final decision takeaway must directly address the
business decision.

8. Do not fabricate sources.

9. Keep the analysis practical for a business decision-maker.

10. Return ONLY JSON.
"""


# ============================================================
# OPENAI RESEARCH
# ============================================================

response = client.responses.create(
    model="gpt-5.6-luna",
    tools=[
        {
            "type": "web_search",
            "search_context_size": "low"
        }
    ],
    input=research_prompt
)


# ============================================================
# PARSE STRUCTURED RESULT
# ============================================================

raw_output = response.output_text.strip()

try:
    research_data = json.loads(raw_output)

except json.JSONDecodeError:

    print("\nSAGE could not parse the structured response.")
    print("\nRaw response:\n")
    print(raw_output)

    raise SystemExit(
        "\nPlease run the research again."
    )


# ============================================================
# SAVE JSON
# ============================================================

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

research_data["_metadata"] = {
    "generated": timestamp,
    "business_problem": business_problem,
    "target_market": target_market,
    "business_decision": business_decision
}


with open(
    "sage_research_data.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        research_data,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# COMPLETION
# ============================================================

print("=" * 70)
print("              SAGE V2 RESEARCH COMPLETE")
print("=" * 70)

print("\nStructured research data saved as:")
print("sage_research_data.json")

print("\nSAGE V2 is ready.")