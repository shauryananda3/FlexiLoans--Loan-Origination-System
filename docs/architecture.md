# Architecture Notes

```text
Customer UI
   |
   v
API / Application Service
   |
   +--> KYC Integration
   +--> Credit/Bureau Integration
   +--> Fraud/PEP Integration
   +--> Business Rule Engine
   +--> Document Service
   +--> E-Sign / E-Mandate
   +--> Disbursement
   |
   +--> Audit / Operational Data
```

This repository intentionally uses one FastAPI application and SQLite to remain easy to run. A production implementation would normally separate concerns into deployable services/modules, use managed relational storage, secrets management, observability, stronger authentication/authorization, secure networking, queues/eventing where appropriate, resilience patterns, CI/CD, automated testing, backup/DR and formal compliance/security review.
