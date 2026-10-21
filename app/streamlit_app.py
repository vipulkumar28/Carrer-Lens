import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.career_engine import (
    calculate_role_match,
    get_career_domains,
    get_roles_for_domain,
    recommend_roles,
)
from src.prediction_engine import predict_placement
from src.roadmap_engine import generate_role_roadmap
from src.role_gap_engine import (
    calculate_role_experience_gaps,
    calculate_role_skill_gaps,
)
from src.skill_gap_engine import (
    calculate_overall_readiness_gaps,
    calculate_overall_readiness_score,
)
from src.skill_profile_engine import (
    build_skill_profile,
    get_skills_for_domain,
)

PROJECT_TITLE = "CareerLens"
PROJECT_SUBTITLE = (
    "End-to-End ML-Based Placement Prediction, "
    "Explainable Skill-Gap Analysis"
)

BRANCH_OPTIONS = [
    "CSE",
    "IT",
    "ECE",
    "EEE",
    "Mechanical",
    "Civil",
]

GENDER_OPTIONS = [
    "Male",
    "Female",
]

COLLEGE_TIER_OPTIONS = [
    "Tier 1",
    "Tier 2",
    "Tier 3",
]

VOLUNTEER_OPTIONS = [
    "Yes",
    "No",
]


st.set_page_config(
    page_title="CareerLens",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
        );

        .stApp {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(
                135deg,
                #f8fbff 0%,
                #eef5ff 50%,
                #ffffff 100%
            );
        }

        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 2.5rem;
            border-radius: 24px;
            color: white;
            background: linear-gradient(
                135deg,
                #0f172a 0%,
                #172554 50%,
                #2563eb 100%
            );
            box-shadow: 0 18px 45px rgba(37, 99, 235, 0.22);
            margin-bottom: 1.5rem;
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin: 0;
        }

        .hero-subtitle {
            max-width: 850px;
            margin-top: 0.7rem;
            color: #dbeafe;
            font-size: 1.05rem;
            line-height: 1.7;
        }

        .section-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            margin: 0.8rem 0 1.2rem 0;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }

        .section-title {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }

        .section-caption {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .footer {
            color: #64748b;
            text-align: center;
            font-size: 0.82rem;
            padding-top: 2rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        div.stButton > button {
            min-height: 3rem;
            border-radius: 10px;
            font-weight: 700;
        }

        div[data-testid="stProgress"] {
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def initialize_session_state():
    defaults = {
        "profile_step": 0,
        "profile_draft": {},
        "analysis_complete": False,
        "analysis_profile": None,
        "analysis_result": None,
        "analysis_scores": None,
        "analysis_overall_gaps": None,
        "analysis_role_gaps": None,
        "analysis_experience_gaps": None,
        "analysis_role_match": None,
        "analysis_roadmap": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_profile():
    st.session_state.profile_step = 0
    st.session_state.profile_draft = {}
    st.session_state.analysis_complete = False
    st.session_state.analysis_profile = None
    st.session_state.analysis_result = None
    st.session_state.analysis_scores = None
    st.session_state.analysis_overall_gaps = None
    st.session_state.analysis_role_gaps = None
    st.session_state.analysis_experience_gaps = None
    st.session_state.analysis_role_match = None
    st.session_state.analysis_roadmap = None

def display_sidebar():
    with st.sidebar:
        st.markdown("## 🎓 CareerLens")
        st.caption("Career readiness intelligence")

        st.divider()

        st.markdown("### CareerLens workflow")
        st.markdown(
            """
            1. Complete academic profile
            2. Explore a career domain
            3. Choose a target role
            4. Rate role-relevant skills
            5. Analyze readiness and gaps
            """
        )

        st.divider()

        st.markdown("### Analysis layers")
        st.markdown(
            """
            - Placement prediction
            - Overall readiness
            - Career match
            - Role-specific gaps
            - Personalized roadmap
            """
        )

        st.divider()

        if st.button(
            "↺ Start a New Assessment",
            use_container_width=True,
        ):
            reset_profile()
            st.rerun()

        st.divider()

        st.markdown("### Important")
        st.caption(
            "CareerLens is an academic decision-support project. "
            "It does not guarantee placement, job selection, or employment."
        )

def get_draft_value(name, default):
    return st.session_state.profile_draft.get(name, default)


def save_draft_values(values):
    st.session_state.profile_draft.update(values)


def safe_select_index(options, current_value):
    if current_value in options:
        return options.index(current_value)

    return 0

def number_input(
    label,
    minimum,
    maximum,
    default,
    step,
    key,
    help_text=None,
):
    return st.number_input(
        label,
        min_value=minimum,
        max_value=maximum,
        value=default,
        step=step,
        key=key,
        help=help_text,
    )

def collect_academic_step():
    draft = st.session_state.profile_draft

    with st.form("academic_profile_form"):
        st.markdown("#### Academic and personal information")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = number_input(
                "Age",
                18,
                24,
                get_draft_value("age", 21),
                1,
                "academic_age",
            )

            cgpa = number_input(
                "CGPA",
                4.5,
                10.0,
                get_draft_value("cgpa", 7.5),
                0.01,
                "academic_cgpa",
            )

        with col2:
            gender = st.selectbox(
                "Gender",
                GENDER_OPTIONS,
                index=safe_select_index(
                    GENDER_OPTIONS,
                    get_draft_value("gender", "Male"),
                ),
                key="academic_gender",
            )

            branch = st.selectbox(
                "Academic Branch",
                BRANCH_OPTIONS,
                index=safe_select_index(
                    BRANCH_OPTIONS,
                    get_draft_value("branch", "CSE"),
                ),
                key="academic_branch",
            )

        with col3:
            college_tier = st.selectbox(
                "College Tier",
                COLLEGE_TIER_OPTIONS,
                index=safe_select_index(
                    COLLEGE_TIER_OPTIONS,
                    get_draft_value("college_tier", "Tier 2"),
                ),
                key="academic_college_tier",
            )

            attendance = number_input(
                "Attendance Percentage",
                50.0,
                100.0,
                get_draft_value("attendance_percentage", 85.0),
                0.1,
                "academic_attendance",
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            backlogs = number_input(
                "Backlogs",
                0,
                6,
                get_draft_value("backlogs", 0),
                1,
                "academic_backlogs",
            )

        with col2:
            sleep_hours = number_input(
                "Sleep Hours",
                3.0,
                10.0,
                get_draft_value("sleep_hours", 7.0),
                0.1,
                "academic_sleep_hours",
            )

        with col3:
            study_hours = number_input(
                "Study Hours Per Day",
                0.5,
                10.0,
                get_draft_value("study_hours_per_day", 3.5),
                0.1,
                "academic_study_hours",
            )

        st.markdown("---")

        _, next_column = st.columns([3, 1])

        with next_column:
            next_clicked = st.form_submit_button(
                "Next →",
                type="primary",
                use_container_width=True,
            )

    if next_clicked:
        save_draft_values(
            {
                "age": age,
                "cgpa": cgpa,
                "gender": gender,
                "branch": branch,
                "college_tier": college_tier,
                "attendance_percentage": attendance,
                "backlogs": backlogs,
                "sleep_hours": sleep_hours,
                "study_hours_per_day": study_hours,
            }
        )

        st.session_state.profile_step = 1
        st.rerun()

def collect_career_step():
    draft = st.session_state.profile_draft
    domains = get_career_domains()

    saved_domain = draft.get(
        "career_domain",
        domains[0],
    )

    if saved_domain not in domains:
        saved_domain = domains[0]

    st.markdown("#### Career exploration")

    st.caption(
        "Career exploration is independent from the placement dataset. "
        "Choose any career domain. CareerLens will show academic "
        "compatibility instead of hiding career opportunities."
    )

    career_domain = st.selectbox(
        "Career Domain",
        domains,
        index=domains.index(saved_domain),
        key="career_domain_selector",
    )

    available_roles = get_roles_for_domain(career_domain)

    if not available_roles:
        st.error(
            f"No roles are configured for the domain: {career_domain}"
        )
        return

    saved_role = draft.get(
        "preferred_role",
        available_roles[0],
    )

    if saved_role not in available_roles:
        saved_role = available_roles[0]

    selected_role_key = (
        f"career_role_selector_{career_domain}"
    )

    preferred_role = st.selectbox(
        "Target Role",
        available_roles,
        index=available_roles.index(saved_role),
        key=selected_role_key,
    )

    st.info(
        f"{career_domain} has {len(available_roles)} "
        "configured role(s)."
    )

    st.markdown("---")

    previous_column, next_column = st.columns(2)

    with previous_column:
        previous_clicked = st.button(
            "← Previous",
            use_container_width=True,
            key="career_previous_button",
        )

    with next_column:
        next_clicked = st.button(
            "Next →",
            type="primary",
            use_container_width=True,
            key="career_next_button",
        )

    if previous_clicked:
        st.session_state.profile_step = 0
        st.rerun()

    if next_clicked:
        st.session_state.profile_draft.update(
            {
                "career_domain": career_domain,
                "preferred_role": preferred_role,
            }
        )

        st.session_state.profile_step = 2
        st.rerun()

def collect_skills_step():
    draft = st.session_state.profile_draft
    domain = draft.get("career_domain", get_career_domains()[0])
    relevant_skills = get_skills_for_domain(domain)

    saved_skill_values = draft.get(
        "technical_skill_values",
        {},
    )

    with st.form("skills_profile_form"):
        st.markdown("#### Overall readiness assessments")

        st.caption(
            "These general assessments are used for overall readiness. "
            "They are separate from the role-specific technical skills below."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            aptitude = number_input(
                "Aptitude Score",
                20.0,
                100.0,
                get_draft_value("aptitude_score", 65.0),
                0.1,
                "skills_aptitude",
            )

        with col2:
            communication = number_input(
                "Communication Skill Score",
                20.0,
                100.0,
                get_draft_value(
                    "communication_skill_score",
                    68.0,
                ),
                0.1,
                "skills_communication",
            )

        with col3:
            logical_reasoning = number_input(
                "Logical Reasoning Score",
                20.0,
                100.0,
                get_draft_value(
                    "logical_reasoning_score",
                    66.0,
                ),
                0.1,
                "skills_logical_reasoning",
            )

            mock_interview = number_input(
                "Mock Interview Score",
                20.0,
                100.0,
                get_draft_value(
                    "mock_interview_score",
                    70.0,
                ),
                0.1,
                "skills_mock_interview",
            )

        st.markdown("---")
        st.markdown("#### Role-specific technical skill profile")

        st.caption(
            "Rate only the skills relevant to your selected career domain. "
            "These values are used for career matching, role-specific gaps, "
            "and the roadmap. They are not inserted into the existing "
            "placement ML model."
        )

        technical_skill_values = {}
        skill_columns = st.columns(2)

        for index, skill in enumerate(relevant_skills):
            default_skill_value = int(
                saved_skill_values.get(skill, 50)
            )

            with skill_columns[index % 2]:
                technical_skill_values[skill] = st.slider(
                    skill,
                    min_value=0,
                    max_value=100,
                    value=default_skill_value,
                    step=5,
                    key=f"domain_skill_{domain}_{skill}",
                )

        st.markdown("---")

        previous_column, next_column = st.columns(2)

        with previous_column:
            previous_clicked = st.form_submit_button(
                "← Previous",
                use_container_width=True,
            )

        with next_column:
            next_clicked = st.form_submit_button(
                "Next →",
                type="primary",
                use_container_width=True,
            )

    if previous_clicked:
        st.session_state.profile_step = 1
        st.rerun()

    if next_clicked:
        technical_skill_profile = build_skill_profile(
            domain,
            technical_skill_values,
        )

        save_draft_values(
            {
                "aptitude_score": aptitude,
                "communication_skill_score": communication,
                "logical_reasoning_score": logical_reasoning,
                "mock_interview_score": mock_interview,
                "technical_skill_values": technical_skill_values,
                "technical_skill_profile": technical_skill_profile,
            }
        )

        st.session_state.profile_step = 3
        st.rerun()

def collect_experience_step():
    draft = st.session_state.profile_draft
    branch = draft.get("branch", "CSE")
    requires_tech_portfolio = branch in {"CSE", "IT", "ECE", "EEE"}

    with st.form("experience_profile_form"):
        st.markdown("#### Experience and professional activity")

        col1, col2, col3 = st.columns(3)

        with col1:
            internships = number_input(
                "Internships Count",
                0,
                8,
                get_draft_value("internships_count", 1),
                1,
                "experience_internships",
            )

            projects = number_input(
                "Projects Count",
                0,
                13,
                get_draft_value("projects_count", 3),
                1,
                "experience_projects",
            )

            certifications = number_input(
                "Certifications Count",
                0,
                11,
                get_draft_value("certifications_count", 2),
                1,
                "experience_certifications",
            )

        with col2:
            extracurricular = number_input(
                "Extracurricular Score",
                0.0,
                100.0,
                get_draft_value("extracurricular_score", 60.0),
                0.1,
                "experience_extracurricular",
            )

            leadership = number_input(
                "Leadership Score",
                0.0,
                100.0,
                get_draft_value("leadership_score", 55.0),
                0.1,
                "experience_leadership",
            )

            volunteer_experience = st.selectbox(
                "Volunteer Experience",
                VOLUNTEER_OPTIONS,
                index=safe_select_index(
                    VOLUNTEER_OPTIONS,
                    get_draft_value(
                        "volunteer_experience",
                        "No",
                    ),
                ),
                key="experience_volunteer",
            )

        with col3:
            if requires_tech_portfolio:
                coding_skill_score = number_input(
                    "Coding / Programming Assessment Score",
                    20.0,
                    100.0,
                    get_draft_value(
                        "coding_skill_score",
                        70.0,
                    ),
                    0.1,
                    "experience_coding_score",
                    help_text=(
                        "Required by the current branch-specific "
                        "placement model for this branch."
                    ),
                )

                hackathons = number_input(
                    "Hackathons / Technical Events",
                    0,
                    8,
                    get_draft_value(
                        "hackathons_participated",
                        1,
                    ),
                    1,
                    "experience_hackathons",
                )

                github_repos = number_input(
                    "GitHub Repositories",
                    0,
                    16,
                    get_draft_value("github_repos", 4),
                    1,
                    "experience_github",
                )

                linkedin_connections = number_input(
                    "LinkedIn Connections",
                    50,
                    999,
                    get_draft_value(
                        "linkedin_connections",
                        500,
                    ),
                    1,
                    "experience_linkedin",
                )
            else:
                st.info(
                    "Coding, hackathons, GitHub, and LinkedIn are not "
                    "shown as general readiness requirements for this "
                    "branch. They are not used in Overall Career Readiness."
                )

                coding_skill_score = get_draft_value(
                    "coding_skill_score",
                    50.0,
                )
                hackathons = get_draft_value(
                    "hackathons_participated",
                    0,
                )
                github_repos = get_draft_value(
                    "github_repos",
                    0,
                )
                linkedin_connections = get_draft_value(
                    "linkedin_connections",
                    50,
                )

        st.markdown("---")

        previous_column, analyze_column = st.columns(2)

        with previous_column:
            previous_clicked = st.form_submit_button(
                "← Previous",
                use_container_width=True,
            )

        with analyze_column:
            analyze_clicked = st.form_submit_button(
                "🔍 Analyze My Career Readiness",
                type="primary",
                use_container_width=True,
            )

    if previous_clicked:
        st.session_state.profile_step = 2
        st.rerun()

    if analyze_clicked:
        save_draft_values(
            {
                "internships_count": internships,
                "projects_count": projects,
                "certifications_count": certifications,
                "extracurricular_score": extracurricular,
                "leadership_score": leadership,
                "volunteer_experience": volunteer_experience,
                "coding_skill_score": coding_skill_score,
                "hackathons_participated": hackathons,
                "github_repos": github_repos,
                "linkedin_connections": linkedin_connections,
            }
        )

        return True

    return False

def build_complete_profile():
    draft = st.session_state.profile_draft

    domain = draft.get(
        "career_domain",
        get_career_domains()[0],
    )

    available_roles = get_roles_for_domain(domain)

    default_role = (
        available_roles[0]
        if available_roles
        else "Not Selected"
    )

    return {
        "age": draft.get("age", 21),
        "cgpa": draft.get("cgpa", 7.5),
        "gender": draft.get("gender", "Male"),
        "branch": draft.get("branch", "CSE"),
        "college_tier": draft.get("college_tier", "Tier 2"),
        "internships_count": draft.get("internships_count", 1),
        "projects_count": draft.get("projects_count", 3),
        "certifications_count": draft.get(
            "certifications_count",
            2,
        ),
        "coding_skill_score": draft.get(
            "coding_skill_score",
            50.0,
        ),
        "aptitude_score": draft.get("aptitude_score", 65.0),
        "communication_skill_score": draft.get(
            "communication_skill_score",
            68.0,
        ),
        "logical_reasoning_score": draft.get(
            "logical_reasoning_score",
            66.0,
        ),
        "hackathons_participated": draft.get(
            "hackathons_participated",
            0,
        ),
        "github_repos": draft.get("github_repos", 0),
        "linkedin_connections": draft.get(
            "linkedin_connections",
            50,
        ),
        "mock_interview_score": draft.get(
            "mock_interview_score",
            70.0,
        ),
        "attendance_percentage": draft.get(
            "attendance_percentage",
            85.0,
        ),
        "backlogs": draft.get("backlogs", 0),
        "extracurricular_score": draft.get(
            "extracurricular_score",
            60.0,
        ),
        "leadership_score": draft.get(
            "leadership_score",
            55.0,
        ),
        "volunteer_experience": draft.get(
            "volunteer_experience",
            "No",
        ),
        "sleep_hours": draft.get("sleep_hours", 7.0),
        "study_hours_per_day": draft.get(
            "study_hours_per_day",
            3.5,
        ),
        "career_domain": domain,
        "preferred_role": draft.get(
            "preferred_role",
            default_role,
        ),
        "technical_skill_profile": draft.get(
            "technical_skill_profile",
            {},
        ),
    }

def collect_profile():
    step = st.session_state.profile_step
    step_names = [
        "Academic Profile",
        "Career Direction",
        "Skills Profile",
        "Experience",
    ]

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-title">Build your CareerLens profile</div>
        <div class="section-caption">
        Complete each step in sequence. Your values remain saved while you
        move backward or forward through the assessment.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"### Step {step + 1} of 4: {step_names[step]}"
    )
    st.progress((step + 1) / 4)

    analyze_clicked = False

    if step == 0:
        collect_academic_step()
    elif step == 1:
        collect_career_step()
    elif step == 2:
        collect_skills_step()
    else:
        analyze_clicked = collect_experience_step()

    st.markdown("</div>", unsafe_allow_html=True)

    return build_complete_profile(), analyze_clicked

def display_prediction(result):
    prediction = result["prediction"]
    probability = result["probability"]
    branch_model = result["branch_model"]

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("1. Placement Prediction")

    col1, col2, col3 = st.columns(3)

    with col1:
        if prediction == 1:
            st.success("Likely to be placed")
        else:
            st.warning("Needs further improvement")

    with col2:
        st.metric(
            "Placement Probability",
            f"{probability * 100:.2f}%",
        )

    with col3:
        confidence = (
            "Higher confidence"
            if probability >= 0.75 or probability <= 0.25
            else "Moderate confidence"
        )

        st.metric("Model Signal", confidence)

    st.caption(
        f"Prediction generated using the {branch_model} "
        "branch-specific placement model."
    )

    st.caption(
        "This ML prediction uses only features available in the placement "
        "training dataset. Role-specific skill ratings are intentionally "
        "excluded because the model was not trained with them."
    )

    st.caption(
        "This is an educational estimate, not a guaranteed placement outcome."
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_readiness_dashboard(scores):
    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("2. Overall Career Readiness")

    st.caption(
        "General employability analysis based on academics, aptitude, "
        "communication, interview readiness, and practical experience."
    )

    score_items = list(scores.items())
    metric_columns = st.columns(len(score_items))

    for column, (label, score) in zip(metric_columns, score_items):
        with column:
            st.metric(label, f"{score:.1f}%")

    chart_data = pd.DataFrame(
        {
            "Readiness Area": [
                label
                for label in scores
                if label != "Overall"
            ],
            "Score": [
                score
                for label, score in scores.items()
                if label != "Overall"
            ],
        }
    ).set_index("Readiness Area")

    st.bar_chart(
        chart_data,
        y="Score",
        color="#2563eb",
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_overall_readiness_gaps(overall_gaps):
    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("3. Overall Readiness Gaps")

    st.caption(
        "These are general career-readiness factors. Technical tools such as "
        "Python, SQL, AutoCAD, SolidWorks, or BIM are intentionally excluded "
        "from this table because they belong to role-specific analysis."
    )

    gap_frame = pd.DataFrame(overall_gaps)

    st.dataframe(
        gap_frame,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_career_match(role_match):
    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("4. Career Match")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Selected Role",
            role_match["role"],
        )

    with col2:
        st.metric(
            "Overall Role Match",
            f"{role_match['overall_match']:.1f}%",
        )

    with col3:
        st.metric(
            "Technical Skill Match",
            f"{role_match['technical_match']:.1f}%",
        )

    with col4:
        st.metric(
            "Experience Match",
            f"{role_match['experience_match']:.1f}%",
        )

    compatibility = role_match["academic_compatibility"]

    if compatibility["label"] == "Strong":
        st.success(
            f"Academic Compatibility: Strong — "
            f"{compatibility['message']}"
        )
    elif compatibility["label"] == "Transferable":
        st.info(
            f"Academic Compatibility: Transferable — "
            f"{compatibility['message']}"
        )
    else:
        st.warning(
            f"Academic Compatibility: Limited — "
            f"{compatibility['message']}"
        )

    st.caption(
        "Career exploration is broader than the placement dataset. "
        "This result is a transparent requirement-based role-fit estimate."
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_role_specific_gaps(skill_gaps, experience_gaps, role):
    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("5. Role-Specific Gap Analysis")

    st.caption(
        f"Selected role: {role}. These gaps compare your self-rated "
        "role-relevant skills with the configured role requirements."
    )

    st.markdown("#### Technical skill gaps")

    st.dataframe(
        pd.DataFrame(skill_gaps),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Role-relevant experience gaps")

    st.dataframe(
        pd.DataFrame(experience_gaps),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Technical skill gaps are not used by the current placement ML model. "
        "They are used only for role matching and personalized guidance."
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_role_recommendations(profile):
    skill_profile = profile["technical_skill_profile"]

    recommendations = recommend_roles(
        profile,
        skill_profile,
        top_n=5,
    )

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("Career Exploration: Top Role Matches")

    recommendation_rows = []

    for item in recommendations:
        recommendation_rows.append(
            {
                "Career Domain": item["domain"],
                "Role": item["role"],
                "Overall Match": f"{item['overall_match']:.1f}%",
                "Academic Compatibility": (
                    item["academic_compatibility"]["label"]
                ),
                "Technical Match": f"{item['technical_match']:.1f}%",
                "Experience Match": f"{item['experience_match']:.1f}%",
            }
        )

    st.dataframe(
        pd.DataFrame(recommendation_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "These roles are shown for exploration. A role is not hidden merely "
        "because it is not the typical academic pathway."
    )

    st.markdown("</div>", unsafe_allow_html=True)

def display_roadmap(roadmap):
    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("6. Personalized Role Roadmap")

    st.caption(
        "The roadmap prioritizes your largest technical skill gaps for the "
        "selected role."
    )

    for index, item in enumerate(roadmap, start=1):
        title = (
            f"Priority {index}: {item['Skill']} "
            f"({item['Priority']})"
        )

        with st.expander(title, expanded=index == 1):
            st.write(
                f"**Current score:** {item['Current']}  |  "
                f"**Required score:** {item['Required']}  |  "
                f"**Gap:** {item['Gap']}"
            )

            st.markdown("**Recommended actions**")

            for action in item["Actions"]:
                st.write(f"- {action}")

    st.markdown("</div>", unsafe_allow_html=True)

def create_report(
    profile,
    result,
    readiness_scores,
    overall_gaps,
    role_match,
    role_skill_gaps,
    experience_gaps,
    roadmap,
):
    prediction_label = (
        "Likely to be placed"
        if result["prediction"] == 1
        else "Needs further improvement"
    )

    lines = [
        "CAREERLENS CAREER READINESS REPORT",
        "=" * 72,
        PROJECT_SUBTITLE,
        "",
        "PROFILE",
        "-" * 72,
        f"Academic Branch: {profile['branch']}",
        f"Career Domain: {profile['career_domain']}",
        f"Target Role: {profile['preferred_role']}",
        f"CGPA: {profile['cgpa']}",
        "",
        "PLACEMENT PREDICTION",
        "-" * 72,
        f"Result: {prediction_label}",
        f"Placement Probability: {result['probability'] * 100:.2f}%",
        f"Branch Model Used: {result['branch_model']}",
        "",
        "OVERALL CAREER READINESS",
        "-" * 72,
    ]

    for label, score in readiness_scores.items():
        lines.append(f"{label}: {score:.1f}%")

    lines.extend(
        [
            "",
            "OVERALL READINESS GAPS",
            "-" * 72,
        ]
    )

    for gap in overall_gaps:
        lines.append(
            f"{gap['Area']}: current={gap['Current']}, "
            f"target={gap['Target']}, "
            f"gap={gap['Gap']}, "
            f"priority={gap['Priority']}"
        )

    lines.extend(
        [
            "",
            "CAREER MATCH",
            "-" * 72,
            f"Selected Role: {role_match['role']}",
            f"Overall Role Match: {role_match['overall_match']:.1f}%",
            (
                "Academic Compatibility: "
                f"{role_match['academic_compatibility']['label']}"
            ),
            f"Technical Skill Match: {role_match['technical_match']:.1f}%",
            f"Experience Match: {role_match['experience_match']:.1f}%",
            "",
            "ROLE-SPECIFIC TECHNICAL GAPS",
            "-" * 72,
        ]
    )

    for gap in role_skill_gaps:
        lines.append(
            f"{gap['Skill']}: current={gap['Current']}, "
            f"required={gap['Required']}, "
            f"gap={gap['Gap']}, "
            f"priority={gap['Priority']}"
        )

    lines.extend(
        [
            "",
            "ROLE-RELEVANT EXPERIENCE GAPS",
            "-" * 72,
        ]
    )

    for gap in experience_gaps:
        lines.append(
            f"{gap['Area']}: current={gap['Current']}, "
            f"required={gap['Required']}, "
            f"gap={gap['Gap']}, "
            f"priority={gap['Priority']}"
        )

    lines.extend(
        [
            "",
            "PERSONALIZED ROADMAP",
            "-" * 72,
        ]
    )

    for index, item in enumerate(roadmap, start=1):
        lines.append(
            f"Priority {index}: {item['Skill']} "
            f"({item['Priority']})"
        )

        for action in item["Actions"]:
            lines.append(f"- {action}")

        lines.append("")

    lines.extend(
        [
            "DISCLAIMER",
            "-" * 72,
            "CareerLens is an educational decision-support project.",
            "Placement probability is an ML estimate based on the available",
            "training dataset and does not guarantee employment.",
            "Role-specific technical skill ratings are used only for career",
            "matching and roadmap guidance, not by the existing ML model.",
        ]
    )

    return "\n".join(lines)

def run_analysis(profile):
    with st.spinner(
        "CareerLens is analyzing your profile and generating insights...",
        show_time=True,
    ):
        time.sleep(0.5)

        result = predict_placement(profile)

        readiness_scores = calculate_overall_readiness_score(
            profile
        )

        overall_gaps = calculate_overall_readiness_gaps(profile)

        role_match = calculate_role_match(
            profile,
            profile["technical_skill_profile"],
            profile["career_domain"],
            profile["preferred_role"],
        )

        role_skill_gaps = calculate_role_skill_gaps(
            profile["technical_skill_profile"],
            profile["career_domain"],
            profile["preferred_role"],
        )

        experience_gaps = calculate_role_experience_gaps(
            profile,
            profile["career_domain"],
            profile["preferred_role"],
        )

        roadmap = generate_role_roadmap(
            role_skill_gaps,
            profile["preferred_role"],
        )

        time.sleep(0.3)

    st.session_state.analysis_complete = True
    st.session_state.analysis_profile = profile
    st.session_state.analysis_result = result
    st.session_state.analysis_scores = readiness_scores
    st.session_state.analysis_overall_gaps = overall_gaps
    st.session_state.analysis_role_gaps = role_skill_gaps
    st.session_state.analysis_experience_gaps = experience_gaps
    st.session_state.analysis_role_match = role_match
    st.session_state.analysis_roadmap = roadmap

def display_analysis_results():
    profile = st.session_state.analysis_profile
    result = st.session_state.analysis_result
    readiness_scores = st.session_state.analysis_scores
    overall_gaps = st.session_state.analysis_overall_gaps
    role_skill_gaps = st.session_state.analysis_role_gaps
    experience_gaps = st.session_state.analysis_experience_gaps
    role_match = st.session_state.analysis_role_match
    roadmap = st.session_state.analysis_roadmap

    display_prediction(result)
    display_readiness_dashboard(readiness_scores)
    display_overall_readiness_gaps(overall_gaps)
    display_career_match(role_match)
    display_role_specific_gaps(
        role_skill_gaps,
        experience_gaps,
        profile["preferred_role"],
    )
    display_role_recommendations(profile)
    display_roadmap(roadmap)

    report = create_report(
        profile,
        result,
        readiness_scores,
        overall_gaps,
        role_match,
        role_skill_gaps,
        experience_gaps,
        roadmap,
    )

    st.markdown(
        '<div class="section-card">',
        unsafe_allow_html=True,
    )

    st.subheader("Download Your CareerLens Report")

    st.download_button(
        label="📄 Download Career Readiness Report",
        data=report,
        file_name="career_lens_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

def main():
    initialize_session_state()
    inject_custom_css()
    display_sidebar()

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">🎓 {PROJECT_TITLE}</div>
            <div class="hero-subtitle">
                {PROJECT_SUBTITLE}. Assess placement readiness within the
                ML model's scope, explore careers, identify role-specific
                skills, and receive a practical improvement roadmap.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    profile, analyze_clicked = collect_profile()

    if analyze_clicked:
        try:
            run_analysis(profile)
            st.rerun()

        except FileNotFoundError:
            st.error(
                f"No branch-specific placement model was found for "
                f"{profile['branch']}. Run: "
                "`python -m src.train_branch_models`"
            )

        except ValueError as error:
            st.error(f"Analysis input error: {error}")

        except KeyError as error:
            st.error(
                f"Career catalog configuration error: missing key {error}. "
                "Check `data/career_catalog.json` and the corresponding "
                "engine files."
            )

    if st.session_state.analysis_complete:
        display_analysis_results()

    st.markdown(
        f"""
        <div class="footer">
            {PROJECT_TITLE}<br>
            Academic end-to-end machine-learning project.
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()