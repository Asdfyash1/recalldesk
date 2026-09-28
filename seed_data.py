"""Synthetic but realistic demo data for Cloudline (project-management SaaS).

Dates are in September 2026 so the demo's '3 days ago' / 'last week' references
feel real. Generated to look like genuine support history.
"""

CUSTOMERS = [
    {
        "id": "priya",
        "name": "Priya Sharma",
        "email": "priya@brightlabs.in",
        "plan": "Scale",
        "company": "BrightLabs",
        "notes": "Engineering manager, 45-person team. Primary demo customer.",
    },
    {
        "id": "arjun",
        "name": "Arjun Mehta",
        "email": "arjun@finlytics.co",
        "plan": "Starter",
        "company": "Finlytics",
        "notes": "Solo founder. Secondary customer for depth.",
    },
    {
        "id": "sara",
        "name": "Sara Thomas",
        "email": "sara@nordwind.de",
        "plan": "Enterprise",
        "company": "Nordwind",
        "notes": "IT admin, 500 seats. Secondary customer for depth.",
    },
]

TICKETS = {
    "priya": [
        {
            "id": "CL-1042",
            "date": "2026-09-12",
            "title": "SSO login loop after v4.2 update",
            "body": ("After the v4.2 update the whole team got stuck in a login loop via "
                     "Okta SSO. Clearing the IdP cache in Cloudline Settings > SSO resolved it. "
                     "Customer confirmed all 45 seats working again."),
            "status": "resolved",
            "resolution": "Cleared IdP cache in Settings > SSO; advised team to re-authenticate once.",
        },
        {
            "id": "CL-1187",
            "date": "2026-09-20",
            "title": "Question about API rate limits",
            "body": ("Customer asked about API rate limits for their Jira sync integration. "
                     "Told them the Scale plan allows 1,000 requests/min per API key and "
                     "burst to 1,500. Shared the rate-limit headers doc."),
            "status": "resolved",
            "resolution": "Explained Scale plan limits (1,000 req/min, burst 1,500); linked docs.",
        },
        {
            "id": "CL-1291",
            "date": "2026-09-24",
            "title": "Dashboard loading very slowly",
            "body": ("Customer reports the main dashboard takes 40+ seconds to load since "
                     "yesterday morning. Found a stuck background worker on their workspace "
                     "(worker w-8812). Re-queued it from Settings > Diagnostics and load time "
                     "dropped to 3 seconds. Customer was frustrated; CSAT 2/5. Promised a "
                     "follow-up check within a week."),
            "status": "resolved",
            "resolution": ("Re-queued stuck worker w-8812 via Settings > Diagnostics. "
                          "Promised proactive follow-up within a week."),
        },
    ],
    "arjun": [
        {
            "id": "CL-1103",
            "date": "2026-09-15",
            "title": "Cannot invite teammate — seat limit",
            "body": ("Customer on Starter plan (5 seats) tried to invite a 6th teammate. "
                     "Explained the seat limit and he upgraded one seat; invite went through."),
            "status": "resolved",
            "resolution": "Added one extra seat to Starter plan; invite succeeded.",
        },
        {
            "id": "CL-1266",
            "date": "2026-09-22",
            "title": "Export to CSV missing custom fields",
            "body": ("CSV export omitted custom fields. Known limitation on Starter; "
                     "workaround is the JSON export which includes everything. Customer "
                     "accepted the workaround."),
            "status": "resolved",
            "resolution": "Workaround: use JSON export for custom fields. Feature request filed.",
        },
    ],
    "sara": [
        {
            "id": "CL-0988",
            "date": "2026-09-08",
            "title": "SCIM provisioning errors with Entra ID",
            "body": ("SCIM provisioning from Entra ID failing for 12 users with error "
                     "E_PROVISION_409. Root cause: duplicate email aliases. Cleaned aliases, "
                     "re-ran sync, all 500 seats provisioned."),
            "status": "resolved",
            "resolution": "Cleaned duplicate email aliases in Entra ID; re-ran SCIM sync.",
        },
        {
            "id": "CL-1210",
            "date": "2026-09-21",
            "title": "Audit log retention question",
            "body": ("Customer asked how long audit logs are retained on Enterprise. "
                     "Answered: 7 years, exportable to SIEM via the Audit API. They need it "
                     "for ISO 27001 certification."),
            "status": "resolved",
            "resolution": "Confirmed 7-year retention + SIEM export; shared ISO 27001 mapping doc.",
        },
    ],
}
