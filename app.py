import streamlit as st
import subprocess
import sys
import json
import os
from pathlib import Path


# =========================================================
# SAGE CONFIGURATION
# =========================================================

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="SAGE | Business Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- Global ---------- */

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- Header ---------- */

    .sage-header {
        padding: 1.5rem 0 1rem 0;
    }

    .sage-logo {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 0;
    }

    .sage-tagline {
        font-size: 1.15rem;
        color: #64748b;
        margin-top: -5px;
    }

    .sage-description {
        font-size: 1rem;
        color: #475569;
        max-width: 850px;
        line-height: 1.7;
        margin-top: 1rem;
    }

    /* ---------- Section headers ---------- */

    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #4f46e5;
        margin-bottom: 0.35rem;
    }

    .section-title {
        font-size: 1.65rem;
        font-weight: 750;
        color: #111827;
        margin-top: 0;
        margin-bottom: 0.75rem;
    }

    /* ---------- Cards ---------- */

    .info-card {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        margin-bottom: 1rem;
    }

    .summary-card {
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #f8fafc;
        line-height: 1.7;
        margin-bottom: 1.25rem;
    }

    .opportunity-card {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #dbeafe;
        background: #f8fbff;
        margin-bottom: 1rem;
    }

    .risk-card {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #fee2e2;
        background: #fffafa;
        margin-bottom: 1rem;
    }

    .action-card {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        margin-bottom: 1rem;
    }

    .source-card {
        padding: 1rem 1.15rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: #fafafa;
        margin-bottom: 0.75rem;
    }

    /* ---------- Badges ---------- */

    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .badge-blue {
        background: #eef2ff;
        color: #4338ca;
    }

    .badge-red {
        background: #fef2f2;
        color: #b91c1c;
    }

    .badge-green {
        background: #ecfdf5;
        color: #047857;
    }

    /* ---------- Footer ---------- */

    .sage-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.82rem;
        padding-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="sage-header">

        <div class="sage-logo">🔎 SAGE</div>

        <div class="sage-tagline">
            Strategic Analysis & Guided Exploration
        </div>

        <div class="sage-description">
            An AI-powered business intelligence agent that researches
            business problems, analyzes market evidence, identifies
            opportunities and risks, and converts research into
            actionable strategic recommendations.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# RESEARCH BRIEF
# =========================================================

st.markdown(
    '<div class="section-label">01 — Research Brief</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">What do you want SAGE to investigate?</div>',
    unsafe_allow_html=True
)

st.write(
    "Give SAGE a clear business problem and the decision you need to make."
)

col1, col2 = st.columns(2)

with col1:

    business_problem = st.text_area(
        "Business Problem",
        placeholder=(
            "Example: Should a new coffee shop brand target "
            "college students in Hyderabad?"
        ),
        height=150
    )

with col2:

    business_decision = st.text_area(
        "Business Decision",
        placeholder=(
            "Example: Decide whether to launch, identify the "
            "target segment, and determine positioning and pricing."
        ),
        height=150
    )

target_market = st.text_input(
    "Target Market",
    placeholder="Example: India - Hyderabad"
)


# =========================================================
# RESEARCH BUTTON
# =========================================================

st.write("")

research_button = st.button(
    "🚀  Start SAGE Research",
    type="primary",
    use_container_width=True
)


# =========================================================
# RESEARCH ENGINE
# =========================================================

if research_button:

    if not business_problem.strip():

        st.warning(
            "Please enter the business problem before starting research."
        )
        st.stop()

    if not target_market.strip():

        st.warning(
            "Please enter the target market before starting research."
        )
        st.stop()

    if not business_decision.strip():

        st.warning(
            "Please enter the business decision before starting research."
        )
        st.stop()

    project_folder = Path(__file__).resolve().parent

    agent_file = project_folder / "agent_v2.py"
    data_file = project_folder / "sage_research_data.json"

    if data_file.exists():
        data_file.unlink()

    st.divider()

    st.markdown(
        '<div class="section-label">02 — SAGE Research Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">SAGE is investigating your problem</div>',
        unsafe_allow_html=True
    )

    progress = st.progress(5)

    status = st.empty()

    try:

        status.info(
            "🔎 Understanding the business problem..."
        )

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

            status.empty()

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

            status.empty()

            st.error(
                "SAGE completed the process, but no research data was generated."
            )

            with st.expander("Technical details"):
                st.code(process.stdout)

            st.stop()

        status.success(
            "✅ Research complete — SAGE has generated the intelligence report."
        )

        progress.progress(100)

        research_data = json.loads(
            data_file.read_text(
                encoding="utf-8"
            )
        )

        st.divider()


        # =================================================
        # EXECUTIVE SUMMARY
        # =================================================

        st.markdown(
            '<div class="section-label">03 — Executive Intelligence</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Executive Summary</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="summary-card">
                {research_data.get(
                    "executive_summary",
                    "No executive summary available."
                )}
            </div>
            """,
            unsafe_allow_html=True
        )


        # =================================================
        # KEY FINDINGS
        # =================================================

        st.markdown(
            '<div class="section-title">Key Findings</div>',
            unsafe_allow_html=True
        )

        findings = research_data.get(
            "key_findings",
            []
        )

        cols = st.columns(
            min(len(findings), 3)
            if findings
            else 1
        )

        for index, finding in enumerate(findings):

            with cols[index % len(cols)]:

                st.markdown(
                    f"""
                    <div class="info-card">
                        <strong>Finding {index + 1}</strong>
                        <br><br>
                        {finding}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # =================================================
        # MARKET OVERVIEW
        # =================================================

        st.markdown(
            '<div class="section-label">04 — Market Intelligence</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Market Overview</div>',
            unsafe_allow_html=True
        )

        market = research_data.get(
            "market_overview",
            {}
        )

        market_col1, market_col2, market_col3 = st.columns(3)

        with market_col1:

            st.markdown("### Market Characteristics")

            for item in market.get(
                "market_characteristics",
                []
            ):
                st.markdown(f"- {item}")

        with market_col2:

            st.markdown("### Demand Patterns")

            for item in market.get(
                "demand_patterns",
                []
            ):
                st.markdown(f"- {item}")

        with market_col3:

            st.markdown("### Important Developments")

            for item in market.get(
                "important_developments",
                []
            ):
                st.markdown(f"- {item}")


        # =================================================
        # CUSTOMER INSIGHTS
        # =================================================

        st.markdown(
            '<div class="section-title">Customer Insights</div>',
            unsafe_allow_html=True
        )

        customers = research_data.get(
            "customer_insights",
            []
        )

        for customer in customers:

            with st.expander(
                f"👥 {customer.get('segment', 'Customer Segment')}",
                expanded=True
            ):

                customer_col1, customer_col2 = st.columns(2)

                with customer_col1:

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

                with customer_col2:

                    st.markdown("**Pain Points**")

                    for item in customer.get(
                        "pain_points",
                        []
                    ):
                        st.markdown(f"- {item}")

                    st.markdown(
                        "**Price Sensitivity**"
                    )

                    st.write(
                        customer.get(
                            "price_sensitivity",
                            "Not specified"
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


        # =================================================
        # COMPETITIVE LANDSCAPE
        # =================================================

        st.markdown(
            '<div class="section-label">05 — Competitive Intelligence</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Competitive Landscape</div>',
            unsafe_allow_html=True
        )

        competitors = research_data.get(
            "competitive_landscape",
            []
        )

        for competitor in competitors:

            with st.expander(
                f"🏢 {competitor.get('competitor', 'Competitor')}"
            ):

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

                comp_col1, comp_col2 = st.columns(2)

                with comp_col1:

                    st.markdown("**Strengths**")

                    for item in competitor.get(
                        "strengths",
                        []
                    ):
                        st.markdown(f"- {item}")

                with comp_col2:

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

                    st.markdown("**Evidence**")

                    for item in evidence:
                        st.markdown(f"- {item}")


        # =================================================
        # TRENDS
        # =================================================

        st.markdown(
            '<div class="section-label">06 — Market Signals</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Market Trends</div>',
            unsafe_allow_html=True
        )

        trends = research_data.get(
            "market_trends",
            []
        )

        for trend in trends:

            st.markdown(
                f"""
                <div class="info-card">
                    <strong>{trend.get('trend', 'Trend')}</strong>
                    <br><br>
                    <strong>Evidence:</strong>
                    {trend.get('evidence', 'Not specified')}
                    <br><br>
                    <strong>Business Implication:</strong>
                    {trend.get('business_implication', 'Not specified')}
                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # OPPORTUNITIES
        # =================================================

        st.markdown(
            '<div class="section-label">07 — Strategic Opportunities</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Opportunities</div>',
            unsafe_allow_html=True
        )

        opportunities = research_data.get(
            "opportunities",
            []
        )

        for opportunity in opportunities:

            st.markdown(
                f"""
                <div class="opportunity-card">

                    <span class="badge badge-blue">
                        OPPORTUNITY
                    </span>

                    <h4>
                        {opportunity.get(
                            "opportunity",
                            "Opportunity"
                        )}
                    </h4>

                    <strong>Why it matters</strong>

                    <p>
                        {opportunity.get(
                            "why_it_matters",
                            "Not specified"
                        )}
                    </p>

                    <strong>Evidence</strong>

                    <p>
                        {opportunity.get(
                            "evidence",
                            "Not specified"
                        )}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # RISKS
        # =================================================

        st.markdown(
            '<div class="section-title">Risks</div>',
            unsafe_allow_html=True
        )

        risks = research_data.get(
            "risks",
            []
        )

        for risk in risks:

            st.markdown(
                f"""
                <div class="risk-card">

                    <span class="badge badge-red">
                        RISK
                    </span>

                    <h4>
                        {risk.get(
                            "risk",
                            "Risk"
                        )}
                    </h4>

                    <strong>Why it matters</strong>

                    <p>
                        {risk.get(
                            "why_it_matters",
                            "Not specified"
                        )}
                    </p>

                    <strong>Evidence</strong>

                    <p>
                        {risk.get(
                            "evidence",
                            "Not specified"
                        )}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # RESEARCH QUALITY
        # =================================================

        st.markdown(
            '<div class="section-label">08 — Evidence Assessment</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Research Quality</div>',
            unsafe_allow_html=True
        )

        quality = research_data.get(
            "evidence_quality",
            {}
        )

        quality_col1, quality_col2 = st.columns(2)

        with quality_col1:

            st.markdown("### Strong Findings")

            for item in quality.get(
                "strong_findings",
                []
            ):
                st.markdown(f"- {item}")

            st.markdown("### Reasonable Findings")

            for item in quality.get(
                "reasonable_findings",
                []
            ):
                st.markdown(f"- {item}")

        with quality_col2:

            st.markdown("### Uncertain Findings")

            for item in quality.get(
                "uncertain_findings",
                []
            ):
                st.markdown(f"- {item}")

            st.markdown("### Research Limitations")

            for item in quality.get(
                "research_limitations",
                []
            ):
                st.markdown(f"- {item}")


        # =================================================
        # STRATEGIC INSIGHTS
        # =================================================

        st.markdown(
            '<div class="section-label">09 — Strategic Intelligence</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Strategic Insights</div>',
            unsafe_allow_html=True
        )

        insights = research_data.get(
            "strategic_insights",
            []
        )

        for index, insight in enumerate(insights):

            st.markdown(
                f"""
                <div class="info-card">

                    <strong>
                        Insight {index + 1}
                    </strong>

                    <p>
                        {insight}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # RECOMMENDED ACTIONS
        # =================================================

        st.markdown(
            '<div class="section-label">10 — Action Plan</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Recommended Actions</div>',
            unsafe_allow_html=True
        )

        actions = research_data.get(
            "recommended_actions",
            []
        )

        for action in actions:

            st.markdown(
                f"""
                <div class="action-card">

                    <span class="badge badge-green">
                        {action.get(
                            "priority",
                            "PRIORITY"
                        )}
                    </span>

                    <h4>
                        {action.get(
                            "action",
                            "Action"
                        )}
                    </h4>

                    <strong>Reason</strong>

                    <p>
                        {action.get(
                            "reason",
                            "Not specified"
                        )}
                    </p>

                    <strong>Expected Impact</strong>

                    <p>
                        {action.get(
                            "expected_impact",
                            "Not specified"
                        )}
                    </p>

                    <strong>Implementation Note</strong>

                    <p>
                        {action.get(
                            "implementation_note",
                            "Not specified"
                        )}
                    </p>

                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # DECISION TAKEAWAY
        # =================================================

        st.markdown(
            '<div class="section-label">11 — Decision Brief</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Decision Takeaway</div>',
            unsafe_allow_html=True
        )

        st.info(
            research_data.get(
                "decision_takeaway",
                "No decision takeaway available."
            )
        )


        # =================================================
        # SOURCES
        # =================================================

        st.markdown(
            '<div class="section-label">12 — Evidence Sources</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Sources</div>',
            unsafe_allow_html=True
        )

        sources = research_data.get(
            "sources",
            []
        )

        for source in sources:

            st.markdown(
                f"""
                <div class="source-card">

                    <strong>
                        {source.get(
                            "source",
                            "Source"
                        )}
                    </strong>

                    <br>

                    Organization:
                    {source.get(
                        "organization",
                        "Not specified"
                    )}

                    <br>

                    Supports:
                    {source.get(
                        "information_supported",
                        "Not specified"
                    )}

                </div>
                """,
                unsafe_allow_html=True
            )


        # =================================================
        # EXPORT
        # =================================================

        st.markdown(
            '<div class="section-label">13 — Export</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">Take Your Research With You</div>',
            unsafe_allow_html=True
        )

        json_download = json.dumps(
            research_data,
            indent=2,
            ensure_ascii=False
        )

        st.download_button(
            label="⬇️ Download Research Data (JSON)",
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


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div class="sage-footer">

        <strong>SAGE</strong>
        · Strategic Analysis & Guided Exploration

        <br>

        AI-powered business research and intelligence

    </div>
    """,
    unsafe_allow_html=True
)