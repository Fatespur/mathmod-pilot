---
name: submission-governance
description: CUMCM/MCM Phase 1 to Phase 3 submission hardening, deep anonymity scanning, bibliography validation, and cryptographic package authorization.
version: 1.0.0
---

# Submission Governance Skill

Comprehensive governance gate for mathematical modeling competitions (CUMCM/MCM).

## Capabilities
1. **Anonymity Deep Scan (H1-B)**: Scans PDF and DOCX documents for metadata leaks, author identifiers, school names, comments, and tracked revisions.
2. **Package Gate & Whitelist Staging (H1-C)**: Enforces manifest-bound whitelist copy and detects unauthorized extra files.
3. **Authorization & Seal (H1-E)**: Enforces cryptographic hash binding (Ed25519) and detects tampering post-freeze.

## Usage
```python
from mathmod_pilot.governance.submission_anonymity_validator import scan_document
from mathmod_pilot.governance.submission_package_validator import validate_package
```
