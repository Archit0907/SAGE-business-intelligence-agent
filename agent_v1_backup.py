from openai import OpenAI
from datetime import datetime

# ============================================================
# SAGE - BUSINESS RESEARCH AGENT
# ============================================================

client = OpenAI(timeout=120.0)

print("\n" + "=" * 70)
print("                 SAGE BUSINESS RESEARCH AGENT")
print("=" * 70)

print("\nSAGE turns a business problem into")
print("research-backed insights and recommendations.\n")


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


# ============================================================
# START RESEARCH
# ============================================================

print("\n" + "=" * 70)
print("                    SAGE RESEARCH STARTED")
print("=" * 70)

print("\n[1/5] Understanding the business problem...")
print("[2/5] Validating the underlying assumptions...")
print("[3/5] Researching the market and competitive landscape...")
print("[4/5] Evaluating evidence and identifying insights...")
print("[5/5] Preparing the final business report...\n")


# ============================================================
# RESEARCH PROMPT
# ============================================================

research_prompt = f"""
You are SAGE, an AI-powered business research agent.

Your role is to independently research a business problem and turn
reliable evidence into useful business insights and recommendations.

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
RESEARCH OBJECTIVE
============================================================

Research the problem deeply enough to help a business decision-maker
understand what is happening, why it is happening, what evidence
supports the conclusion, and what actions could reasonably be taken.

Do NOT simply accept the premise of the business problem.

First determine whether the assumption behind the problem is actually
supported by available evidence.

============================================================
REPORT STRUCTURE
============================================================

Create the report using these sections:

# 1. Executive Summary

Give a concise summary of the most important findings and their
business implications.

# 2. Business Problem

Clearly define the business problem and explain what decision the
research is intended to support.

# 3. Premise Validation

Critically examine the assumptions contained in the original business
problem.

Explain:

- What assumptions are being made?
- Which assumptions are supported by evidence?
- Which assumptions are uncertain?
- What evidence contradicts or qualifies the premise?

Do not treat the original question as an established fact.

# 4. Market Overview

Analyze the relevant market in the specified target market.

Include important:

- Market characteristics
- Customer behavior
- Demand patterns
- Market developments
- Recent changes

Use recent information wherever possible.

# 5. Customer / Consumer Insights

Identify relevant customer segments and explain:

- Customer needs
- Purchase drivers
- Price sensitivity
- Behavioral patterns
- Pain points
- Important differences between segments

# 6. Competitive Landscape

Identify relevant competitors, alternatives, substitutes, or competing
business models.

Compare them based on meaningful factors such as:

- Pricing
- Value proposition
- Customer segment
- Distribution
- Product/service offering
- Competitive strengths
- Competitive gaps

# 7. Key Market Trends

Identify important recent trends that could affect the business.

For each major trend explain:

- What is happening?
- What evidence supports it?
- Why does it matter?

# 8. Research Quality & Evidence

Evaluate the quality of the research.

Separate findings into:

A. Strongly supported findings
B. Reasonably supported findings
C. Uncertain or limited-evidence findings

Also identify important research limitations.

Do not present weak evidence as established fact.

# 9. Strategic Insights

Translate the research into business implications.

Explain:

- What the company should understand
- What opportunities exist
- What risks exist
- What assumptions still need testing
- What could create competitive advantage

# 10. Recommended Actions

Provide practical and actionable recommendations.

Prioritize them where appropriate.

For each recommendation explain:

- Recommended action
- Reason
- Expected business impact
- Important implementation consideration

Avoid generic advice.

# 11. Final Business Takeaway

Give a concise conclusion answering the business decision question.

The conclusion must reflect the evidence and acknowledge uncertainty
where appropriate.

# 12. Sources

List the important sources used during the research.

For each source provide:

- Source name
- Publication or organization
- What information it supported

============================================================
RESEARCH RULES
============================================================

1. Use reliable and recent web sources.

2. Prefer primary sources, official company information,
government sources, industry reports, academic research, and
reputable business publications.

3. Cross-check important claims whenever possible.

4. Clearly distinguish facts from analysis and recommendations.

5. Do not invent statistics, companies, market figures, or sources.

6. If reliable evidence is unavailable for a claim, explicitly say so.

7. Do not assume that correlation proves causation.

8. Pay attention to the target market specified by the user.

9. Use the business decision to determine what information is
commercially relevant.

10. Keep the report practical and useful for real business
decision-making.

============================================================
FINAL QUALITY CHECK
============================================================

Before producing the final report, verify that:

- The business problem was directly addressed.
- The original premise was critically examined.
- The target market was respected.
- Important claims are supported by evidence.
- Competing explanations were considered.
- Recommendations logically follow from the research.
- Uncertainty and limitations are clearly stated.
- Sources are clearly identified.

Return ONLY the completed research report.
"""


# ============================================================
# OPENAI RESPONSE
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
# SAVE REPORT
# ============================================================

report = response.output_text

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

header = f"""# SAGE BUSINESS RESEARCH REPORT

**Generated:** {timestamp}

---

## Business Problem

{business_problem}

## Target Market

{target_market}

## Business Decision

{business_decision}

---

"""


final_report = header + report


# TXT FILE

with open("research_report.txt", "w", encoding="utf-8") as file:
    file.write(final_report)


# MARKDOWN FILE

with open("research_report.md", "w", encoding="utf-8") as file:
    file.write(final_report)


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print("=" * 70)
print("                    RESEARCH COMPLETE!")
print("=" * 70)

print("\nSAGE completed:")
print("- Business problem analysis")
print("- Premise validation")
print("- Market research")
print("- Customer insights")
print("- Competitive analysis")
print("- Trend analysis")
print("- Evidence evaluation")
print("- Strategic insights")
print("- Business recommendations")

print("\nFiles created:")
print("- research_report.txt")
print("- research_report.md")

print("\nSAGE is ready for the next business problem.")