from app.services.engineering_comparison_service import (
    compare_finding_categories,
)


previous_findings = [
    {
        "title": "Database credentials pending",
        "description": "Database credentials are unavailable.",
        "evidence": ["Waiting for database credentials"],
        "severity": "high",
    },
    {
        "title": "Authentication endpoint failing",
        "description": "Authentication is blocking integration testing.",
        "evidence": ["Authentication endpoint failing"],
        "severity": "medium",
    },
]

latest_findings = [
    {
        "title": "Authentication endpoint failing",
        "description": "Authentication is blocking integration testing.",
        "evidence": ["Authentication endpoint failing"],
        "severity": "medium",
    },
    {
        "title": "Cache configuration incomplete",
        "description": "Cache configuration is blocking testing.",
        "evidence": ["Cache configuration blocking performance testing"],
        "severity": "medium",
    },
]

result = compare_finding_categories(
    previous_findings=previous_findings,
    latest_findings=latest_findings,
)

print("\nENGINEERING COMPARISON TEST")
print("===========================")

print("\nNEWLY INTRODUCED:")
for finding in result.newly_introduced:
    print(finding.title)

print("\nRESOLVED:")
for finding in result.resolved:
    print(finding.title)

print("\nPERSISTENT:")
for finding in result.persistent:
    print(finding.title)

assert len(result.newly_introduced) == 1
assert len(result.resolved) == 1
assert len(result.persistent) == 1

print("\nAll comparison tests passed.")