def build_report(
    profile,
    prediction_result,
    readiness,
    role,
    role_match,
    gaps,
    roadmap,
):
    lines = [
        "CAREERLENS CAREER READINESS REPORT",
        "=" * 65,
        "",
        "PROFILE",
        "-" * 65,
        f"Branch: {profile['branch']}",
        f"Career Path: {profile['career_path']}",
        f"Preferred Role: {role}",
        f"CGPA: {profile['cgpa']}",
        "",
        "PLACEMENT PREDICTION",
        "-" * 65,
        (
            "Prediction: Placed"
            if prediction_result["prediction"] == 1
            else "Prediction: Not Placed"
        ),
        (
            f"Estimated probability: "
            f"{prediction_result['probability'] * 100:.2f}%"
        ),
        "",
        "CAREER READINESS",
        "-" * 65,
    ]

    for label, score in readiness.items():
        lines.append(f"{label}: {score:.1f}%")

    lines.extend(
        [
            "",
            "CAREER MATCH",
            "-" * 65,
            f"Role: {role}",
            f"Role match score: {role_match:.2f}%",
            "",
            "SKILL GAPS",
            "-" * 65,
        ]
    )

    if gaps:
        for gap in gaps:
            lines.append(
                f"{gap['Area']}: current={gap['Current']}, "
                f"required={gap['Required']}, "
                f"priority={gap['Priority']}"
            )
    else:
        lines.append("No major skill gaps detected.")

    lines.extend(
        [
            "",
            "ROADMAP",
            "-" * 65,
        ]
    )

    for phase, tasks in roadmap.items():
        lines.append(f"\n{phase}")

        for task in tasks:
            lines.append(f"- {task}")

    lines.extend(
        [
            "",
            "DISCLAIMER",
            "-" * 65,
            "CareerLens is an educational decision-support system.",
            "It does not guarantee placement or employment.",
        ]
    )

    return "\n".join(lines)