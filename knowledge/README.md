# Approved public knowledge workflow

AI-03 stores public knowledge as versioned JSON, not as unreviewed website scrapes.

1. Create a draft entry with a public HTTPS source and a unique stable ID.
2. Confirm its factual accuracy, policy status and publication dates against the official site.
3. Have an authorised Delnavazan reviewer set `approved_by` and `status=approved`.
4. Review a PR containing the approval; only approved and currently effective entries can be retrieved.
5. Retire or supersede outdated entries; preserve Git history.

The included example entries are deliberately **draft** and will not be supplied to the model.
Retrieval is deterministic keyword matching, not semantic search. Persian synonyms,
Finglish normalization, trusted-source allowlisting, injection-resistant rendering,
and confidence thresholds require additional work before production.

No internal admin pages, student data, teacher personal data, payments or private
WordPress endpoints are permitted in the public knowledge catalogue.
