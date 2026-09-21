import streamlit as st
import subprocess
import sys
import json
import os
from pathlib import Path


# ---------------------------------------------------------
# STREAMLIT SECRETS
# ---------------------------------------------------------

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="SAGE | Business Intelligence",
    page_icon="🔎",
    layout="wide"
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🔎 SAGE")
st.subheader("Business Intelligence & Research Agent")

st.write(
    "SAGE researches a business problem, analyzes market evidence, "
    "identifies opportunities and risks, and converts the findings "
    "into actionable business recommendations."
)

st.divider()


# ---------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------

st.header("Research Brief")

business_problem = st.text_area(
    "What business problem should SAGE research?",
    placeholder=(
        "Example: Should a new coffee shop brand target college "
        "students in Hyderabad, and what strategy should it use "
        "to compete with existing cafes?"
    ),
    height=120
)

target_market = st.text_input(
    "Which country or market should SAGE focus on?",
    placeholder="Example: India - Hyderabad"
)

business_decision = st.text_area(
    "What business decision should this research help with?",
    placeholder=(
        "Example: Decide whether to launch the coffee shop and "
        "determine its target segment, positioning, pricing, "
        "and competitive strategy."
    ),
    height=100
)


# ---------------------------------------------------------
# RESEARCH BUTTON
# ---------------------------------------------------------

research_button = st.button(
    "🚀 Research with SAGE",
    type="primary",
    use_container_width=True
)


# ---------------------------------------------------------
# RUN SAGE
# ---------------------------------------------------------

if research_button:

    if not business_problem.strip():
        st.warning("Please enter the business problem.")

    elif not target_market.strip():
        st.warning("Please enter the target market.")

    elif not business_decision.strip():
        st.warning("Please enter the business decision.")

    else:

        project_folder = Path(__file__).resolve().parent
        agent_file = project_folder / "agent_v2.py"
        data_file = project_folder / "sage_research_data.json"

        # Remove previous research output
        if data_file.exists():
            data_file.unlink()

        st.info(
            "SAGE is researching the problem. "
            "This may take a few minutes."
        )

        progress = st.progress(0)

        try:

            progress.progress(15)

            process = subprocess.run(
                [sys.executable, str(agent_file)],
                input=(
                    business_problem
                    + "\n"
                    + target_market
                    + "\n"
                    + business_decision
                    + "\n"
                ),
                text=True,
                capture_output=True,
                cwd=str(project_folder),
                timeout=900
            )

            progress.progress(80)

            if process.returncode != 0:

                st.error(
                    "SAGE encountered an error while conducting the research."
                )

                with st.expander("Technical details"):
                    st.code(
                        process.stderr
                        if process.stderr
                        else process.stdout
                    )

                st.stop()

            if not data_file.exists():

                st.error(
                    "SAGE completed the process, but the research "
                    "data file was not created."
                )

                with st.expander("Technical details"):
                    st.code(process.stdout)

                st.stop()

            research_data = json.loads(
                data_file.read_text(encoding="utf-8")
            )

            progress.progress(100)

            st.success("Research completed successfully! 🎉")

            st.divider()


            # -------------------------------------------------
            # EXECUTIVE SUMMARY
            # -------------------------------------------------

            st.header("📌 Executive Summary")

            st.write(
                research_data.get(
                    "executive_summary",
                    "No executive summary available."
                )
            )


            # -------------------------------------------------
            # KEY FINDINGS
            # -------------------------------------------------

            st.header("🔑 Key Findings")

            for finding in research_data.get("key_findings", []):
                st.markdown(f"- {finding}")


            # -------------------------------------------------
            # MARKET OVERVIEW
            # -------------------------------------------------

            st.header("📊 Market Overview")

            market = research_data.get(
                "market_overview",
                {}
            )

            st.subheader("Market Characteristics")

            for item in market.get(
                "market_characteristics",
                []
            ):
                st.markdown(f"- {item}")

            st.subheader("Demand Patterns")

            for item in market.get(
                "demand_patterns",
                []
            ):
                st.markdown(f"- {item}")

            st.subheader("Important Developments")

            for item in market.get(
                "important_developments",
                []
            ):
                st.markdown(f"- {item}")


            # -------------------------------------------------
            # CUSTOMER INSIGHTS
            # -------------------------------------------------

            st.header("👥 Customer Insights")

            customers = research_data.get(
                "customer_insights",
                []
            )

            for customer in customers:

                st.subheader(
                    customer.get(
                        "segment",
                        "Customer Segment"
                    )
                )

                st.markdown("**Needs**")

                for item in customer.get("needs", []):
                    st.markdown(f"- {item}")

                st.markdown("**Purchase Drivers**")

                for item in customer.get(
                    "purchase_drivers",
                    []
                ):
                    st.markdown(f"- {item}")

                st.markdown("**Pain Points**")

                for item in customer.get(
                    "pain_points",
                    []
                ):
                    st.markdown(f"- {item}")

                st.markdown(
                    "**Price Sensitivity:** "
                    + customer.get(
                        "price_sensitivity",
                        "Not specified"
                    )
                )

                evidence = customer.get(
                    "evidence",
                    []
                )

                if evidence:

                    with st.expander("Evidence"):

                        for item in evidence:
                            st.markdown(f"- {item}")


            # -------------------------------------------------
            # COMPETITIVE LANDSCAPE
            # -------------------------------------------------

            st.header("🏢 Competitive Landscape")

            competitors = research_data.get(
                "competitive_landscape",
                []
            )

            for competitor in competitors:

                st.subheader(
                    competitor.get(
                        "competitor",
                        "Competitor"
                    )
                )

                st.write(
                    "**Type:** "
                    + competitor.get(
                        "type",
                        "Not specified"
                    )
                )

                st.write(
                    "**Value Proposition:** "
                    + competitor.get(
                        "value_proposition",
                        "Not specified"
                    )
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("**Strengths**")

                    for item in competitor.get(
                        "strengths",
                        []
                    ):
                        st.markdown(f"- {item}")

                with col2:

                    st.markdown("**Gaps**")

                    for item in competitor.get(
                        "gaps",
                        []
                    ):
                        st.markdown(f"- {item}")

                st.write(
                    "**Pricing:** "
                    + competitor.get(
                        "pricing",
                        "Not specified"
                    )
                )

                evidence = competitor.get(
                    "evidence",
                    []
                )

                if evidence:

                    with st.expander("Evidence"):

                        for item in evidence:
                            st.markdown(f"- {item}")


            # -------------------------------------------------
            # MARKET TRENDS
            # -------------------------------------------------

            st.header("📈 Market Trends")

            trends = research_data.get(
                "market_trends",
                []
            )

            for trend in trends:

                st.subheader(
                    trend.get(
                        "trend",
                        "Trend"
                    )
                )

                st.write(
                    "**Evidence:** "
                    + trend.get(
                        "evidence",
                        "Not specified"
                    )
                )

                st.write(
                    "**Business Implication:** "
                    + trend.get(
                        "business_implication",
                        "Not specified"
                    )
                )


            # -------------------------------------------------
            # OPPORTUNITIES & RISKS
            # -------------------------------------------------

            st.header("🎯 Opportunities")

            opportunities = research_data.get(
                "opportunities",
                []
            )

            for opportunity in opportunities:

                st.subheader(
                    opportunity.get(
                        "opportunity",
                        "Opportunity"
                    )
                )

                st.write(
                    "**Why it matters:** "
                    + opportunity.get(
                        "why_it_matters",
                        "Not specified"
                    )
                )

                st.write(
                    "**Evidence:** "
                    + opportunity.get(
                        "evidence",
                        "Not specified"
                    )
                )


            st.header("⚠️ Risks")

            risks = research_data.get(
                "risks",
                []
            )

            for risk in risks:

                st.subheader(
                    risk.get(
                        "risk",
                        "Risk"
                    )
                )

                st.write(
                    "**Why it matters:** "
                    + risk.get(
                        "why_it_matters",
                        "Not specified"
                    )
                )

                st.write(
                    "**Evidence:** "
                    + risk.get(
                        "evidence",
                        "Not specified"
                    )
                )


            # -------------------------------------------------
            # RESEARCH QUALITY
            # -------------------------------------------------

            st.header("🔬 Research Quality")

            quality = research_data.get(
                "evidence_quality",
                {}
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Strong Findings")

                for item in quality.get(
                    "strong_findings",
                    []
                ):
                    st.markdown(f"- {item}")

                st.subheader("Reasonable Findings")

                for item in quality.get(
                    "reasonable_findings",
                    []
                ):
                    st.markdown(f"- {item}")

            with col2:

                st.subheader("Uncertain Findings")

                for item in quality.get(
                    "uncertain_findings",
                    []
                ):
                    st.markdown(f"- {item}")

                st.subheader("Research Limitations")

                for item in quality.get(
                    "research_limitations",
                    []
                ):
                    st.markdown(f"- {item}")


            # -------------------------------------------------
            # STRATEGIC INSIGHTS
            # -------------------------------------------------

            st.header("💡 Strategic Insights")

            for insight in research_data.get(
                "strategic_insights",
                []
            ):
                st.markdown(f"- {insight}")


            # -------------------------------------------------
            # RECOMMENDED ACTIONS
            # -------------------------------------------------

            st.header("🚀 Recommended Actions")

            actions = research_data.get(
                "recommended_actions",
                []
            )

            for action in actions:

                st.subheader(
                    action.get(
                        "priority",
                        "Priority"
                    )
                    + " — "
                    + action.get(
                        "action",
                        "Action"
                    )
                )

                st.write(
                    "**Reason:** "
                    + action.get(
                        "reason",
                        "Not specified"
                    )
                )

                st.write(
                    "**Expected Impact:** "
                    + action.get(
                        "expected_impact",
                        "Not specified"
                    )
                )

                st.write(
                    "**Implementation Note:** "
                    + action.get(
                        "implementation_note",
                        "Not specified"
                    )
                )


            # -------------------------------------------------
            # DECISION TAKEAWAY
            # -------------------------------------------------

            st.header("🧭 Decision Takeaway")

            st.info(
                research_data.get(
                    "decision_takeaway",
                    "No decision takeaway available."
                )
            )


            # -------------------------------------------------
            # SOURCES
            # -------------------------------------------------

            st.header("📚 Sources")

            sources = research_data.get(
                "sources",
                []
            )

            for source in sources:

                st.markdown(
                    f"**{source.get('source', 'Source')}**  \n"
                    f"Organization: "
                    f"{source.get('organization', 'Not specified')}  \n"
                    f"Supports: "
                    f"{source.get('information_supported', 'Not specified')}"
                )

                st.divider()


            # -------------------------------------------------
            # DOWNLOAD JSON
            # -------------------------------------------------

            st.header("⬇️ Export Research")

            json_download = json.dumps(
                research_data,
                indent=2,
                ensure_ascii=False
            )

            st.download_button(
                label="Download Research Data (JSON)",
                data=json_download,
                file_name="sage_research_data.json",
                mime="application/json",
                use_container_width=True
            )


        except subprocess.TimeoutExpired:

            st.error(
                "SAGE took too long to complete the research. "
                "Please try again."
            )


        except Exception as e:

            st.error(
                "An unexpected error occurred."
            )

            with st.expander("Technical details"):
                st.code(str(e))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "SAGE — AI-powered business research and intelligence agent"
)