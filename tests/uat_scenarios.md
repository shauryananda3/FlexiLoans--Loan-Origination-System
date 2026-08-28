# UAT Scenarios

| ID | Scenario | Expected Result |
|---|---|---|
| UAT-01 | Valid application | Application created in SUBMITTED |
| UAT-02 | KYC success | State moves to KYC_VERIFIED |
| UAT-03 | CIBIL success | Score stored; state moves to CREDIT_COMPLETED |
| UAT-04 | Eligible decision | BRE moves application to APPROVED |
| UAT-05 | Ineligible decision | Application is rejected/manual-review according to configured rule |
| UAT-06 | Document generation | Required documents generated and status updated |
| UAT-07 | E-sign success | E-sign integration recorded |
| UAT-08 | E-mandate success | State moves to MANDATE_COMPLETED |
| UAT-09 | Disbursement success | Unique disbursement reference recorded; state DISBURSED |
| UAT-10 | CIBIL timeout | Failure recorded; application state preserved; retry/reprocess possible |
| UAT-11 | Invalid stage transition | API returns controlled 409 error |
| UAT-12 | Audit trail | Every major transition has timestamp, actor, old/new status and details |
