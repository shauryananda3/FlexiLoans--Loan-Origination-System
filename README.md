# FlexiLoans LOS — Technical BA Portfolio Prototype

A runnable, educational **Loan Origination System (LOS)** prototype demonstrating how a Business Analyst can translate a digital personal-loan requirement into an implementable end-to-end technology solution.

> **Disclaimer:** This is an educational/portfolio prototype. It does not connect to real CIBIL, KYC, banking, payment, or lending APIs. All integrations and rules are mock/illustrative.

## 1. Project Overview

The prototype simulates a digital personal-loan journey covering:

- Customer onboarding and application creation
- Application lifecycle/state management
- Mock PAN/KYC verification
- Mock CIBIL credit check
- Mock fraud/PEP screening
- Business Rule Engine (BRE) decisioning
- Document generation
- E-Sign
- E-Mandate
- Loan disbursement
- Audit trail and traceability
- Integration failure handling
- Retry/reprocess simulation
- UAT scenarios
- BA interview view

The BA framework demonstrated is:

**Requirement → Process → Rule → API → Data Mapping → Exception → UAT → Audit**

## 2. Business Objective

Enable a fully digital personal-loan journey from application creation through disbursement while ensuring that mandatory validations, integrations, business rules, exception handling, and auditability are clearly defined.

## 3. End-to-End Loan Journey

```text
Application Created
        ↓
SUBMITTED
        ↓
KYC_VERIFIED
        ↓
CREDIT_COMPLETED
        ↓
APPROVED
        ↓
DOCUMENTS_COMPLETED
        ↓
E-SIGN
        ↓
MANDATE_COMPLETED
        ↓
DISBURSED
```

## 4. Application Lifecycle

| Stage | Description |
|---|---|
| SUBMITTED | Customer application created |
| KYC_VERIFIED | KYC validation completed |
| CREDIT_COMPLETED | Credit/risk checks completed |
| APPROVED | BRE approved the application |
| DOCUMENTS_COMPLETED | Loan documents generated |
| MANDATE_COMPLETED | E-Mandate registered |
| DISBURSED | Loan successfully disbursed |

## 5. Business Process

### Application Creation

Customer provides:

- Name
- PAN
- Employment type
- Monthly income
- Requested loan amount
- Tenure

The application starts in `SUBMITTED` state and receives an application number.

### KYC Verification

Mock KYC validates PAN and address.

```json
{
  "pan_verified": true,
  "address_verified": true,
  "provider": "MOCK_CKYC"
}
```

Successful transition:

`SUBMITTED → KYC_VERIFIED`

### Credit Bureau

Mock CIBIL returns a credit score.

```json
{
  "bureau": "MOCK_CIBIL",
  "credit_score": 760,
  "bureau_status": "SUCCESS"
}
```

### Fraud / PEP Screening

Mock risk screening returns an acceptable status such as `CLEAR`.

### BRE Decisioning

Illustrative rule:

```text
IF credit_score >= 750
AND requested_amount <= configured_product_limit
THEN APPROVE
ELSE REJECT
```

Example:

`CREDIT_COMPLETED → BRE_DECISION → APPROVED`

### Documents

After approval, the prototype generates mock:

- Sanction Letter
- Loan Agreement
- Repayment Schedule

Transition:

`APPROVED → DOCUMENTS_COMPLETED`

### E-Sign

Mock digital signature response:

```json
{
  "signature_status": "SIGNED",
  "provider": "MOCK_ESIGN"
}
```

### E-Mandate

Mock repayment mandate response:

```json
{
  "mandate_status": "ACTIVE",
  "provider": "MOCK_MANDATE"
}
```

### Disbursement

Disbursement is permitted only after mandatory fulfilment stages are completed.

Example response:

```json
{
  "reference": "DISB-61E7B8648D",
  "amount": 250000
}
```

Final state: `DISBURSED`

## 6. API / Integration Mapping

| Business Requirement | Integration | Purpose |
|---|---|---|
| Verify identity | KYC API | Identity/KYC verification |
| Obtain credit score | CIBIL API | Credit assessment |
| Screen risk | Fraud/PEP API | Risk screening |
| Determine eligibility | BRE | Credit decision |
| Generate documents | Document service | Loan documentation |
| Digital agreement | E-Sign API | Digital signature |
| Repayment setup | E-Mandate API | Mandate registration |
| Loan payout | Disbursement API | Disbursement |

## 7. Business Rules

1. KYC must be verified before credit processing.
2. Credit processing must complete before BRE decisioning.
3. Credit score must satisfy the configured eligibility threshold.
4. Requested amount must remain within the configured product limit.
5. Fraud/PEP checks must return an acceptable status.
6. Documents must be completed before final fulfilment.
7. E-Sign must be completed before final fulfilment.
8. E-Mandate must be active before disbursement.
9. Disbursement should only occur when mandatory prerequisites are satisfied.

## 8. Exception Handling — CIBIL Timeout

A key BA/system-design scenario is an external integration failure.

```text
CIBIL Timeout
     ↓
Integration Failure Recorded
     ↓
Application State Preserved
     ↓
Failure Marked Retryable
     ↓
Retry / Reprocess
     ↓
CIBIL Success
     ↓
Continue Processing
```

Example integration result:

```json
{
  "error": "TIMEOUT",
  "retryable": true
}
```

The application does not restart from the beginning. This demonstrates separation of **application state** and **integration state**.

## 9. Audit Trail

Every major application transition and integration event is recorded with information such as:

- Timestamp
- Event type
- Previous status
- New status
- Processing details/reason
- Integration result where applicable

Example:

```text
APPLICATION_CREATED | - → SUBMITTED
KYC_COMPLETED | SUBMITTED → KYC_VERIFIED
CREDIT_COMPLETED | KYC_VERIFIED → CREDIT_COMPLETED
BRE_DECISION | CREDIT_COMPLETED → APPROVED
DOCUMENTS_GENERATED | APPROVED → DOCUMENTS_COMPLETED
E_SIGN_COMPLETED | DOCUMENTS_COMPLETED → DOCUMENTS_COMPLETED
MANDATE_COMPLETED | DOCUMENTS_COMPLETED → MANDATE_COMPLETED
DISBURSEMENT_COMPLETED | MANDATE_COMPLETED → DISBURSED
```

## 10. Operations / Integration View

The UI displays mock integration events such as:

```text
KYC | SUCCESS
CIBIL | SUCCESS
FRAUD_PEP | SUCCESS
E_SIGN | SUCCESS
E_MANDATE | SUCCESS
DISBURSEMENT | SUCCESS
```

It also displays failures such as:

```text
CIBIL | FAILED | TIMEOUT | retryable=true
```

## 11. BA Interview View

The application includes a dedicated BA view demonstrating:

```text
Requirement
     ↓
Process
     ↓
Business Rule
     ↓
API
     ↓
Data Mapping
     ↓
Exception
     ↓
UAT
     ↓
Audit
```

This shows how a BA translates a business requirement into implementable system behaviour.

## 12. Business Requirements Demonstrated

**BR-01 — Digital Application:** Customer can submit a personal-loan application digitally.

**BR-02 — KYC Validation:** KYC must complete before credit processing.

**BR-03 — Credit Assessment:** Credit information must be obtained before decisioning.

**BR-04 — Risk Screening:** Fraud/PEP checks must return an acceptable status.

**BR-05 — Eligibility Decision:** BRE evaluates configured eligibility rules.

**BR-06 — Documentation:** Loan documents are generated after approval.

**BR-07 — Digital Agreement:** E-Sign is required before final fulfilment.

**BR-08 — Repayment Mandate:** E-Mandate must be active before disbursement.

**BR-09 — Disbursement:** Loan is disbursed only after mandatory prerequisites are satisfied.

**BR-10 — Auditability:** Major application and integration events are recorded.

## 13. Data / Field Mapping

| UI Field | Backend Field | Purpose |
|---|---|---|
| Name | `name` | Customer name |
| PAN | `pan` | Customer identifier |
| Employment | `employment_type` | Employment category |
| Monthly Income | `income` | Income assessment |
| Requested Amount | `requested_amount` | Loan amount |
| Tenure | `tenure_months` | Loan tenure |

Integration outputs include KYC verification, CIBIL score, fraud status, BRE decision, E-Sign status, E-Mandate status, and disbursement reference.

## 14. UAT — Positive Scenario

**Given:** A valid applicant with successful KYC, CIBIL and fraud checks, an eligible credit score, and an amount within the product limit.

**When:** The BRE evaluates the application.

**Then:** The application is approved and can proceed through:

```text
APPROVED
   ↓
DOCUMENTS_COMPLETED
   ↓
E-SIGN
   ↓
MANDATE_COMPLETED
   ↓
DISBURSED
```

## 15. UAT — CIBIL Timeout Scenario

**Given:** The application has completed KYC and reached credit processing.

**When:** CIBIL times out.

**Then the system should:**

1. Record the integration failure.
2. Mark it retryable.
3. Preserve the application state.
4. Display the recommended action.
5. Allow retry/reprocessing.
6. Continue processing after successful retry.

## 16. Technical Architecture

```text
                ┌──────────────────────┐
                │       Web UI         │
                │    HTML / CSS / JS   │
                └──────────┬───────────┘
                           │ REST APIs
                           ↓
                ┌──────────────────────┐
                │     FastAPI App      │
                │   Business Services  │
                └──────────┬───────────┘
                           │
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        Application       BRE       Integrations
         Lifecycle       Rules         Layer
              └────────────┼────────────┘
                           ↓
                    ┌─────────────┐
                    │  SQLite DB  │
                    └─────────────┘
```

## 17. Technology Stack

- Python
- FastAPI
- Uvicorn
- SQLite
- HTML/CSS/JavaScript
- REST APIs
- JSON
- Mock integrations

## 18. Project Structure

```text
flexiloans-los/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── los.db
│   └── static/
│       └── index.html
│
├── docs/
├── tests/
├── README.md
└── requirements.txt
```

## 19. How to Run

Requires Python 3.10+.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

`http://127.0.0.1:8000`

API docs:

`http://127.0.0.1:8000/docs`

## 20. Suggested Interview Demonstration

1. Create an application.
2. Run KYC.
3. Run CIBIL.
4. Run BRE.
5. Generate documents.
6. Complete E-Sign.
7. Complete E-Mandate.
8. Disburse the loan.
9. Explain the audit trail.
10. Create another application and demonstrate CIBIL timeout/reprocess behaviour.

A strong explanation is:

> "I created a technical BA portfolio prototype for a digital personal-loan origination system. The objective was not to build a production lending platform, but to demonstrate how I translate a business requirement into implementable system behaviour. I mapped the journey from application creation through KYC, credit bureau, fraud checks, BRE decisioning, documentation, e-sign, mandate and disbursement. I also incorporated exception handling for a CIBIL timeout, where the application state is preserved and the integration is marked retryable. Finally, I added audit trails and UAT scenarios to demonstrate traceability and validation."

## 21. BA Capabilities Demonstrated

- Requirements analysis
- Process mapping
- Functional requirements
- Business rules
- API/integration analysis
- Data mapping
- Exception handling
- State management
- UAT design
- Audit/traceability
- Stakeholder communication
- Business-to-technology translation

## 22. BA Deliverables Represented

```text
Business Requirement
        ↓
Process Flow
        ↓
Functional Requirements
        ↓
Business Rules
        ↓
API / Integration Mapping
        ↓
Data Mapping
        ↓
Exception Handling
        ↓
UAT Scenarios
        ↓
Audit / Traceability
```

## 23. Future Enhancements

Potential future improvements:

- Operations dashboard
- Role-based access
- Application search/filtering
- Maker-checker workflow
- Configurable BRE rules
- Product configuration
- Retry counter/history
- SLA monitoring
- Notification service
- PostgreSQL
- Automated test coverage
- Docker deployment
- Cloud deployment
- Authentication and authorization

## 24. Portfolio Value

The project demonstrates that a Business Analyst can bridge business and technology:

```text
Business
 ├── Requirements
 ├── Process
 ├── Rules
 ├── Exceptions
 └── UAT
        ↓
Technical
 ├── APIs
 ├── Data Mapping
 ├── Integrations
 ├── State Management
 └── Audit
        ↓
Implementation
 └── Working Prototype
```

The goal is to demonstrate **business-to-technology translation**, not simply coding ability.

## Author

**Shaurya Nanda**  
Business Analyst / Transformation Professional  
Technical BA Portfolio Project — FlexiLoans LOS
