from openai import OpenAI

client = OpenAI(timeout=120.0)

print("\n" + "=" * 70)
print("                 SAGE BUSINESS RESEARCH AGENT")
print("=" * 70)

# ============================================================
# USER INPUT
# ============================================================

business_problem = input(
    "\nWhat business problem should SAGE research?\n\n> "
)

target_market = input(
    "\nWhich country or market should SAGE focus on?\n\n> "
)

print("\n" + "=" * 70)
print("SAGE WORKFLOW STARTED")
print("=" * 70)


# ============================================================
# STEP 1 — PREMISE VALIDATION
# ============================================================

print("\nSAGE is validating the business assumption...")
print("Please wait...\n")

premise_response = client.responses.create(
    model="gpt-5.6-luna",
    tools=[
        {
            "type": "web_search",
            "search_context_size": "low"
        }
    ],
    input=f"""
You are SAGE, an AI business research agent.

Business problem:
{business_problem}

Target market:
{target_market}

First, validate the assumption contained in the business problem.

Determine:

1. What assumption the question makes.
2. What evidence would be required to prove or disprove it.
3. Whether available evidence currently supports, contradicts, or
   does not establish the assumption.
4. Important limitations or ambiguities in the question.
5. How the research question should be reframed if necessary.

Use recent and reliable sources.

Do NOT jump directly to recommendations.

Clearly distinguish:
- FACTS
- INTERPRETATION
- UNKNOWN / UNVERIFIED

End with a short section called:

PREMISE STATUS
""",
)

premise_validation = premise_response.output_text

print("Premise validation complete.")


# ============================================================
# STEP 2 — RESEARCH PLAN
# ============================================================

print("\nSAGE is creating a research plan...")
print("Please wait...\n")

plan_response = client.responses.create(
    model="gpt-5.6-luna",
    input=f"""
You are SAGE, an AI business research agent.

Business problem:
{business_problem}

Target market:
{target_market}

Premise validation:
{premise_validation}

Create a detailed research plan.

The plan must contain:

1. Core business question
2. Key research questions
3. Information that must be collected
4. Relevant market dimensions
5. Competitor or industry factors to investigate
6. Consumer/customer factors
7. Economic or environmental factors
8. Data gaps and limitations
9. Criteria for determining whether the original assumption
   is supported

Do not answer the research question yet.

Focus only on designing the research.
""",
)

research_plan = plan_response.output_text

print("Research plan created.")


# ============================================================
# STEP 3 — WEB RESEARCH
# ============================================================

print("\nSAGE is conducting the research...")
print("Please wait...\n")

research_response = client.responses.create(
    model="gpt-5.6-luna",
    tools=[
        {
            "type": "web_search",
            "search_context_size": "medium"
        }
    ],
    input=f"""
You are SAGE, an AI business research agent.

Conduct deep web research for the following problem.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

PREMISE VALIDATION:
{premise_validation}

RESEARCH PLAN:
{research_plan}

Research the problem using recent, reliable sources.

Prioritize:
- Government sources
- Regulatory bodies
- Company reports
- Investor reports
- Industry reports
- Academic research
- Reputable business publications
- Reliable market data

Investigate:

1. Market size and growth
2. Consumer/customer behaviour
3. Important market trends
4. Competitors and competitive dynamics
5. Pricing and affordability
6. Technology or distribution factors
7. Major business challenges
8. Emerging opportunities
9. Relevant demographic or geographic differences
10. Evidence supporting or contradicting the original assumption

For every important finding, explain:
- What the evidence says
- Why it matters
- How reliable the evidence appears

Do not invent statistics.

If evidence is unavailable, explicitly say so.

Separate FACTUAL FINDINGS from ANALYSIS.

At the end provide:

KEY RESEARCH FINDINGS

and

SOURCES USED
""",
)

research_findings = research_response.output_text

print("Research completed.")


# ============================================================
# STEP 4 — EVIDENCE EVALUATION
# ============================================================

print("\nSAGE is evaluating the quality of the evidence...")
print("Please wait...\n")

evidence_response = client.responses.create(
    model="gpt-5.6-luna",
    input=f"""
You are SAGE, an evidence evaluation specialist.

Business problem:
{business_problem}

Target market:
{target_market}

Research findings:
{research_findings}

Evaluate the research critically.

For the major findings:

1. Identify the evidence being used.
2. Assess its reliability.
3. Identify possible biases or limitations.
4. Identify contradictions between sources.
5. Identify findings that are strong enough for business decisions.
6. Identify findings that remain uncertain.
7. Identify important information that is still missing.

Do not introduce new facts.

Do not exaggerate confidence.

End with:

EVIDENCE CONFIDENCE
- High confidence findings
- Medium confidence findings
- Low confidence / uncertain findings
""",
)

evidence_evaluation = evidence_response.output_text

print("Evidence evaluation complete.")


# ============================================================
# STEP 5 — FINAL BUSINESS REPORT
# ============================================================

print("\nSAGE is preparing the final business report...")
print("Please wait...\n")

final_response = client.responses.create(
    model="gpt-5.6-luna",
    input=f"""
You are SAGE, an AI-powered business research consultant.

Prepare a professional business research report.

BUSINESS PROBLEM:
{business_problem}

TARGET MARKET:
{target_market}

PREMISE VALIDATION:
{premise_validation}

RESEARCH PLAN:
{research_plan}

RESEARCH FINDINGS:
{research_findings}

EVIDENCE EVALUATION:
{evidence_evaluation}

Create the final report using exactly these sections:

1. Executive Summary

2. Business Problem

3. Premise Validation

4. Market Overview

5. Consumer / Customer Insights

6. Competitive Landscape

7. Key Market Trends

8. Major Challenges

9. Opportunities

10. Strategic Insights

11. Recommended Actions

12. Risks and Limitations

13. Conclusion

14. Sources

IMPORTANT:

- Clearly distinguish facts from analysis.
- Do not treat an unverified assumption as fact.
- Do not invent statistics.
- Mention uncertainty where appropriate.
- Recommendations must directly follow from the evidence.
- Recommendations should be practical and actionable.
- Explain why each major recommendation matters.
- Keep the report useful for an actual business decision-maker.
""",
)

final_report = final_response.output_text

print("Final report prepared.")


# ============================================================
# SAVE REPORTS
# ============================================================

with open("research_report.txt", "w", encoding="utf-8") as file:
    file.write("SAGE BUSINESS RESEARCH REPORT\n")
    file.write("=" * 70 + "\n\n")

    file.write("PREMISE VALIDATION\n")
    file.write("=" * 70 + "\n\n")
    file.write(premise_validation)

    file.write("\n\n" + "=" * 70 + "\n")
    file.write("RESEARCH PLAN\n")
    file.write("=" * 70 + "\n\n")
    file.write(research_plan)

    file.write("\n\n" + "=" * 70 + "\n")
    file.write("RESEARCH FINDINGS\n")
    file.write("=" * 70 + "\n\n")
    file.write(research_findings)

    file.write("\n\n" + "=" * 70 + "\n")
    file.write("EVIDENCE EVALUATION\n")
    file.write("=" * 70 + "\n\n")
    file.write(evidence_evaluation)

    file.write("\n\n" + "=" * 70 + "\n")
    file.write("FINAL BUSINESS REPORT\n")
    file.write("=" * 70 + "\n\n")
    file.write(final_report)


with open("research_report.md", "w", encoding="utf-8") as file:
    file.write("# SAGE BUSINESS RESEARCH REPORT\n\n")

    file.write("## Premise Validation\n\n")
    file.write(premise_validation)

    file.write("\n\n## Research Plan\n\n")
    file.write(research_plan)

    file.write("\n\n## Research Findings\n\n")
    file.write(research_findings)

    file.write("\n\n## Evidence Evaluation\n\n")
    file.write(evidence_evaluation)

    file.write("\n\n## Final Business Report\n\n")
    file.write(final_report)


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 70)
print("                    RESEARCH COMPLETE!")
print("=" * 70)

print("\nSAGE saved:")
print("- Premise validation")
print("- Research plan")
print("- Research findings")
print("- Evidence evaluation")
print("- Final business report")

print("\nFiles created:")
print("- research_report.txt")
print("- research_report.md")

print("\nSAGE is ready for the next business problem.")