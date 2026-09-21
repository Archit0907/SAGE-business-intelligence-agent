import streamlit as st
import subprocess
import sys
from pathlib import Path
import json

# ============================================================
# SAGE - BUSINESS RESEARCH DASHBOARD
# ============================================================

st.set_page_config(
    page_title="SAGE | Business Intelligence",
    page_icon="🔎",
    layout="wide"
)

# ============================================================
# HEADER
# ============================================================

st.title("🔎 SAGE")
st.subheader("AI-Powered Business Intelligence Agent")

st.write(
    "Turn a business problem into research-backed insights, "
    "competitive intelligence and actionable recommendations."
)

st.divider()

# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("## 🎯 Define Your Business Problem")

business_problem = st.text_area(
    "Business Problem",
    placeholder=(
        "Example: Should a new coffee shop target college students "
        "in Hyderabad?"
    ),
    height=100
)

col1, col2 = st.columns(2)

with col1:
    target_market = st.text_input(
        "Target Market",
        placeholder="Example: India - Hyderabad"
    )

with col2:
    business_decision = st.text_input(
        "Business Decision",
        placeholder=(
            "Example: Decide target segment, positioning and pricing."
        )
    )

st.divider()

# ============================================================
# RESEARCH BUTTON
# ============================================================

research_button = st.button(
    "🚀 Research with SAGE",
    type="primary",
    use_container_width=True
)

# ============================================================
# RUN RESEARCH
# ============================================================

if research_button:

    if not business_problem.strip():
        st.warning("Please enter a business problem.")
        st.stop()

    if not target_market.strip():
        st.warning("Please enter a target market.")
        st.stop()

    if not business_decision.strip():
        st.warning("Please enter the business decision.")
        st.stop()

    project_folder = Path(__file__).resolve().parent
    agent_file = project_folder / "agent_v2.py"
    data_file = project_folder / "sage_research_data.json"

    if not agent_file.exists():
        st.error("agent_v2.py was not found.")
        st.stop()

    # Remove previous research data
    if data_file.exists():
        data_file.unlink()

    st.info(
        "🔎 SAGE is researching the market, customers, "
        "competitors and business opportunities..."
    )

    progress = st.progress(0)

    try:

        progress.progress(15)

        process = subprocess.run(
            [sys.executable, str(agent_file)],
            input=(
                business_problem.strip()
                + "\n"
                + target_market.strip()
                + "\n"
                + business_decision.strip()
                + "\n"
            ),
            text=True,
            capture_output=True,
            cwd=str(project_folder),
            timeout=900
        )

        progress.progress(80)

        if process.returncode != 0:

            st.error("SAGE encountered an error.")

            with st.expander("Technical details"):
                st.code(process.stderr)

            st.stop()

        if not data_file.exists():

            st.error(
                "SAGE completed but the structured research "
                "data was not found."
            )

            st.stop()

        research_data = json.loads(
            data_file.read_text(
                encoding="utf-8"
            )
        )

        progress.progress(100)

        st.success(
            "✅ Research completed successfully!"
        )

        st.divider()

        # ====================================================
        # EXECUTIVE SUMMARY
        # ====================================================

        st.markdown("## 📌 Executive Summary")

        st.info(
            research_data.get(
                "executive_summary",
                "No executive summary available."
            )
        )

        # ====================================================
        # KEY FINDINGS
        # ====================================================

        st.markdown("## 🔍 Key Findings")

        findings = research_data.get(
            "key_findings",
            []
        )

        for finding in findings:
            st.markdown(f"- {finding}")

        # ====================================================
        # MARKET OVERVIEW
        # ====================================================

        st.markdown("## 📊 Market Overview")

        market = research_data.get(
            "market_overview",
            {}
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### Market Characteristics")

            for item in market.get(
                "market_characteristics",
                []
            ):
                st.markdown(f"- {item}")

        with col2:

            st.markdown("### Demand Patterns")

            for item in market.get(
                "demand_patterns",
                []
            ):
                st.markdown(f"- {item}")

        with col3:

            st.markdown("### Important Developments")

            for item in market.get(
                "important_developments",
                []
            ):
                st.markdown(f"- {item}")

        # ====================================================
        # CUSTOMER INSIGHTS
        # ====================================================

        st.divider()

        st.markdown("## 👥 Customer Insights")

        customers = research_data.get(
            "customer_insights",
            []
        )

        for customer in customers:

            with st.expander(
                f"👤 {customer.get('segment', 'Customer Segment')}"
            ):

                st.markdown("**Needs**")

                for item in customer.get(
                    "needs",
                    []
                ):
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
                        "Not available"
                    )
                )

                evidence = customer.get(
                    "evidence",
                    []
                )

                if evidence:

                    st.markdown("**Evidence**")

                    for item in evidence:
                        st.markdown(f"- {item}")

        # ====================================================
        # COMPETITIVE LANDSCAPE
        # ====================================================

        st.divider()

        st.markdown("## 🏆 Competitive Landscape")

        competitors = research_data.get(
            "competitive_landscape",
            []
        )

        for competitor in competitors:

            with st.expander(
                f"🏢 {competitor.get('competitor', 'Competitor')}"
            ):

                st.markdown(
                    f"**Type:** "
                    f"{competitor.get('type', 'N/A')}"
                )

                st.markdown(
                    f"**Value Proposition:** "
                    f"{competitor.get('value_proposition', 'N/A')}"
                )

                st.markdown(
                    f"**Pricing:** "
                    f"{competitor.get('pricing', 'N/A')}"
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

                    st.markdown("**Competitive Gaps**")

                    for item in competitor.get(
                        "gaps",
                        []
                    ):
                        st.markdown(f"- {item}")

        # ====================================================
        # MARKET TRENDS
        # ====================================================

        st.divider()

        st.markdown("## 📈 Market Trends")

        trends = research_data.get(
            "market_trends",
            []
        )

        for trend in trends:

            with st.expander(
                f"📈 {trend.get('trend', 'Market Trend')}"
            ):

                st.markdown(
                    f"**Evidence:** "
                    f"{trend.get('evidence', 'N/A')}"
                )

                st.markdown(
                    f"**Business Implication:** "
                    f"{trend.get('business_implication', 'N/A')}"
                )

        # ====================================================
        # OPPORTUNITIES & RISKS
        # ====================================================

        st.divider()

        st.markdown("## 💡 Opportunities & Risks")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### 🚀 Opportunities")

            for opportunity in research_data.get(
                "opportunities",
                []
            ):

                with st.expander(
                    opportunity.get(
                        "opportunity",
                        "Opportunity"
                    )
                ):

                    st.write(
                        "**Why it matters:** "
                        + opportunity.get(
                            "why_it_matters",
                            "N/A"
                        )
                    )

                    st.write(
                        "**Evidence:** "
                        + opportunity.get(
                            "evidence",
                            "N/A"
                        )
                    )

        with col2:

            st.markdown("### ⚠️ Risks")

            for risk in research_data.get(
                "risks",
                []
            ):

                with st.expander(
                    risk.get(
                        "risk",
                        "Risk"
                    )
                ):

                    st.write(
                        "**Why it matters:** "
                        + risk.get(
                            "why_it_matters",
                            "N/A"
                        )
                    )

                    st.write(
                        "**Evidence:** "
                        + risk.get(
                            "evidence",
                            "N/A"
                        )
                    )

        # ====================================================
        # EVIDENCE QUALITY
        # ====================================================

        st.divider()

        st.markdown("## 🧪 Research Quality")

        evidence_quality = research_data.get(
            "evidence_quality",
            {}
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown("### 🟢 Strong Evidence")

            for item in evidence_quality.get(
                "strong_findings",
                []
            ):
                st.markdown(f"- {item}")

        with col2:

            st.markdown("### 🟡 Reasonable Evidence")

            for item in evidence_quality.get(
                "reasonable_findings",
                []
            ):
                st.markdown(f"- {item}")

        with col3:

            st.markdown("### 🔴 Uncertain")

            for item in evidence_quality.get(
                "uncertain_findings",
                []
            ):
                st.markdown(f"- {item}")

        limitations = evidence_quality.get(
            "research_limitations",
            []
        )

        if limitations:

            st.markdown("### Research Limitations")

            for item in limitations:
                st.markdown(f"- {item}")

        # ====================================================
        # STRATEGIC INSIGHTS
        # ====================================================

        st.divider()

        st.markdown("## 🧠 Strategic Insights")

        for insight in research_data.get(
            "strategic_insights",
            []
        ):
            st.markdown(f"- {insight}")

        # ====================================================
        # RECOMMENDED ACTIONS
        # ====================================================

        st.divider()

        st.markdown("## 🎯 Recommended Actions")

        actions = research_data.get(
            "recommended_actions",
            []
        )

        for action in actions:

            priority = action.get(
                "priority",
                "Action"
            )

            with st.expander(
                f"🎯 {priority} — "
                f"{action.get('action', 'Recommended Action')}"
            ):

                st.markdown(
                    f"**Reason:** "
                    f"{action.get('reason', 'N/A')}"
                )

                st.markdown(
                    f"**Expected Impact:** "
                    f"{action.get('expected_impact', 'N/A')}"
                )

                st.markdown(
                    f"**Implementation:** "
                    f"{action.get('implementation_note', 'N/A')}"
                )

        # ====================================================
        # DECISION TAKEAWAY
        # ====================================================

        st.divider()

        st.markdown("## 🧭 Decision Takeaway")

        st.success(
            research_data.get(
                "decision_takeaway",
                "No decision takeaway available."
            )
        )

        # ====================================================
        # SOURCES
        # ====================================================

        st.divider()

        st.markdown("## 📚 Sources")

        sources = research_data.get(
            "sources",
            []
        )

        for source in sources:

            st.markdown(
                f"**{source.get('source', 'Source')}**"
            )

            st.caption(
                f"{source.get('organization', '')} — "
                f"{source.get('information_supported', '')}"
            )

        # ====================================================
        # DOWNLOAD
        # ====================================================

        st.divider()

        json_download = json.dumps(
            research_data,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            "📥 Download Research Data",
            data=json_download,
            file_name="SAGE_Research_Data.json",
            mime="application/json",
            use_container_width=True
        )

    except subprocess.TimeoutExpired:

        st.error(
            "SAGE took longer than expected to complete the research. "
            "Please try again."
        )

    except Exception as e:

        st.error(
            "Something went wrong while running SAGE."
        )

        with st.expander("Technical details"):
            st.code(str(e))


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "SAGE — Business Intelligence Agent | "
    "Evidence → Insights → Decisions"
)