A full Mermaid diagram is maintained at `/docs/architecture.mmd`, reflecting the AWS service map below.

| Concern | AWS Service |
|---|---|
| Device ingestion | AWS IoT Core (MQTT topics per device) |
| Stream processing / fan-out | Amazon Kinesis Data Streams + Firehose (raw archive to S3) |
| Event-driven compute | AWS Lambda (geofence checks, fall detection, alert dispatch) |
| ML model hosting | Amazon SageMaker (real-time endpoints) |
| Optional NLP | Amazon Bedrock |
| Primary data store | Amazon DynamoDB (single-table design) |
| Object storage | Amazon S3 (audio embeddings, reports, QR images) |
| Auth | Amazon Cognito (User Pools + Identity Pools, RBAC) |
| API layer | Amazon API Gateway (REST + WebSocket) fronting FastAPI on ECS Fargate |
| Maps / geolocation | Amazon Location Service |
| Notifications | Amazon SNS, Amazon Pinpoint (SMS/push/OTP) |
| Secrets / keys | AWS KMS + AWS Secrets Manager |
| Monitoring | Amazon CloudWatch + AWS X-Ray |
| CDN / hosting | Amazon CloudFront + AWS Amplify Hosting |
| IaC | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions → AWS CodeDeploy / CDK deploy |
| Compliance / audit | AWS CloudTrail, AWS Config |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18+ (Vite), TypeScript, TailwindCSS, React Query, Zustand/Redux Toolkit, Recharts/D3 |
| Backend | FastAPI (Python 3.11+), Pydantic v2, async SQLAlchemy (optional), Uvicorn/Gunicorn |
| Database | Amazon DynamoDB (primary) + Amazon RDS PostgreSQL (optional, relational reporting only) |
| Cloud | AWS |
| AI/ML | Amazon SageMaker, AWS Lambda, Amazon Bedrock (optional) |
| Auth | Amazon Cognito, JWT, RBAC |
| Real-time | AWS IoT Core → Kinesis → WebSocket API |
| IaC | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions → AWS CodeDeploy / Amplify Hosting + ECS Fargate or Lambda |

## Features

- **Authentication & Access Control** — Cognito login, optional phone OTP (SNS/Pinpoint), roles (`super_admin`, `org_admin`, `caregiver`, `responder`), optional MFA, role-based UI rendering.
- **Real-Time Dashboard** — live map, vitals strip (heart rate, stress index, battery), color-coded alert feed, historical heatmap with playback.
- **Geofencing** — draw-on-map CRUD for safe zones, real-time breach evaluation against incoming GPS pings.
- **AI Stress & Distress Detection** — `/ml/stress-score` and `/ml/distress-classify` endpoints proxying SageMaker; fall detection via lightweight rule+ML hybrid in Lambda.
- **Dynamic Encrypted QR Identity** — rotating KMS-signed JWT QR tokens; tiered public resolution endpoint; every scan logged and pushed to caregivers in real time.
- **Panic Alert** — wearable-triggered SNS fan-out (SMS + push + in-app) with configurable escalation to secondary contacts.
- **Non-Verbal Assist Log** — event-coded need categories rendered as a communication timeline for pattern recognition.
- **Reporting & Analytics** — weekly/monthly PDF/in-app reports, CSV export with consent enforcement.

## Data Model

DynamoDB single-table design — table name: `AutiGuardCore`

| PK | SK | Entity | Notes |
|---|---|---|---|
| `ORG#<orgId>` | `PROFILE` | Organization | name, plan tier |
| `ORG#<orgId>` | `USER#<userId>` | Caregiver/Admin | role, contact info |
| `WEARER#<wearerId>` | `PROFILE` | Wearer profile | name, DOB, medical notes, QR tiering rules |
| `WEARER#<wearerId>` | `TELEMETRY#<ISO8601>` | Time-series ping | HR, GPS, accel summary, stress_index |
| `WEARER#<wearerId>` | `ALERT#<ISO8601>` | Alert event | type, severity, ack status |
| `WEARER#<wearerId>` | `GEOFENCE#<fenceId>` | Safe zone | polygon/radius coords |
| `WEARER#<wearerId>` | `QRSCAN#<ISO8601>` | Scan log | tier resolved, location |
| `WEARER#<wearerId>` | `COMMLOG#<ISO8601>` | Non-verbal event | category code |

- **GSI1** (`GSI1PK = WEARER#<id>`, `GSI1SK = ALERT type`) — efficient cross-time-range alert queries.
- **TTL** enabled on raw telemetry (archived to S3 via Firehose before expiry).
- **DynamoDB Streams** trigger a Lambda for real-time WebSocket push to connected dashboards.

## Repository Structure
Device (wearable) → AWS IoT Core → Kinesis Data Streams → Lambda (compute/ML) → DynamoDB
↘ SageMaker (inference)
DynamoDB Streams → Lambda → WebSocket API (API Gateway) → React Dashboard
FastAPI (ECS Fargate / Lambda) ← API Gateway (REST) ← React Frontend (Amplify/CloudFront)
A full Mermaid diagram is maintained at `/docs/architecture.mmd`, reflecting the AWS service map below.

| Concern | AWS Service |
|---|---|
| Device ingestion | AWS IoT Core (MQTT topics per device) |
| Stream processing / fan-out | Amazon Kinesis Data Streams + Firehose (raw archive to S3) |
| Event-driven compute | AWS Lambda (geofence checks, fall detection, alert dispatch) |
| ML model hosting | Amazon SageMaker (real-time endpoints) |
| Optional NLP | Amazon Bedrock |
| Primary data store | Amazon DynamoDB (single-table design) |
| Object storage | Amazon S3 (audio embeddings, reports, QR images) |
| Auth | Amazon Cognito (User Pools + Identity Pools, RBAC) |
| API layer | Amazon API Gateway (REST + WebSocket) fronting FastAPI on ECS Fargate |
| Maps / geolocation | Amazon Location Service |
| Notifications | Amazon SNS, Amazon Pinpoint (SMS/push/OTP) |
| Secrets / keys | AWS KMS + AWS Secrets Manager |
| Monitoring | Amazon CloudWatch + AWS X-Ray |
| CDN / hosting | Amazon CloudFront + AWS Amplify Hosting |
| IaC | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions → AWS CodeDeploy / CDK deploy |
| Compliance / audit | AWS CloudTrail, AWS Config |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18+ (Vite), TypeScript, TailwindCSS, React Query, Zustand/Redux Toolkit, Recharts/D3 |
| Backend | FastAPI (Python 3.11+), Pydantic v2, async SQLAlchemy (optional), Uvicorn/Gunicorn |
| Database | Amazon DynamoDB (primary) + Amazon RDS PostgreSQL (optional, relational reporting only) |
| Cloud | AWS |
| AI/ML | Amazon SageMaker, AWS Lambda, Amazon Bedrock (optional) |
| Auth | Amazon Cognito, JWT, RBAC |
| Real-time | AWS IoT Core → Kinesis → WebSocket API |
| IaC | AWS CDK (TypeScript) |
| CI/CD | GitHub Actions → AWS CodeDeploy / Amplify Hosting + ECS Fargate or Lambda |

## Features

- **Authentication & Access Control** — Cognito login, optional phone OTP (SNS/Pinpoint), roles (`super_admin`, `org_admin`, `caregiver`, `responder`), optional MFA, role-based UI rendering.
- **Real-Time Dashboard** — live map, vitals strip (heart rate, stress index, battery), color-coded alert feed, historical heatmap with playback.
- **Geofencing** — draw-on-map CRUD for safe zones, real-time breach evaluation against incoming GPS pings.
- **AI Stress & Distress Detection** — `/ml/stress-score` and `/ml/distress-classify` endpoints proxying SageMaker; fall detection via lightweight rule+ML hybrid in Lambda.
- **Dynamic Encrypted QR Identity** — rotating KMS-signed JWT QR tokens; tiered public resolution endpoint; every scan logged and pushed to caregivers in real time.
- **Panic Alert** — wearable-triggered SNS fan-out (SMS + push + in-app) with configurable escalation to secondary contacts.
- **Non-Verbal Assist Log** — event-coded need categories rendered as a communication timeline for pattern recognition.
- **Reporting & Analytics** — weekly/monthly PDF/in-app reports, CSV export with consent enforcement.

## Data Model

DynamoDB single-table design — table name: `AutiGuardCore`

| PK | SK | Entity | Notes |
|---|---|---|---|
| `ORG#<orgId>` | `PROFILE` | Organization | name, plan tier |
| `ORG#<orgId>` | `USER#<userId>` | Caregiver/Admin | role, contact info |
| `WEARER#<wearerId>` | `PROFILE` | Wearer profile | name, DOB, medical notes, QR tiering rules |
| `WEARER#<wearerId>` | `TELEMETRY#<ISO8601>` | Time-series ping | HR, GPS, accel summary, stress_index |
| `WEARER#<wearerId>` | `ALERT#<ISO8601>` | Alert event | type, severity, ack status |
| `WEARER#<wearerId>` | `GEOFENCE#<fenceId>` | Safe zone | polygon/radius coords |
| `WEARER#<wearerId>` | `QRSCAN#<ISO8601>` | Scan log | tier resolved, location |
| `WEARER#<wearerId>` | `COMMLOG#<ISO8601>` | Non-verbal event | category code |

- **GSI1** (`GSI1PK = WEARER#<id>`, `GSI1SK = ALERT type`) — efficient cross-time-range alert queries.
- **TTL** enabled on raw telemetry (archived to S3 via Firehose before expiry).
- **DynamoDB Streams** trigger a Lambda for real-time WebSocket push to connected dashboards.

## Repository Structure
/infra          CDK (TypeScript) stacks: networking, DynamoDB, Cognito, IoT Core,
Lambda, SageMaker endpoint config, API Gateway, CloudFront/Amplify
/backend         FastAPI service (typed, pytest-covered)
/app
/api/v1      auth, wearers, telemetry, alerts, geofence, qr, ml, comms, reports
/core        config, security (Cognito JWKS verification), dynamodb helpers
/services    stress_service, geofence_service, qr_service, notification_service
/schemas     Pydantic models
main.py
/frontend        React + TypeScript app
/docs
architecture.mmd   Mermaid diagram of the AWS service map
api-spec.yaml      OpenAPI 3.1 spec (exported from FastAPI)
README.md
## API Overview

Illustrative endpoint contracts (see `/docs/api-spec.yaml` for the full OpenAPI spec):

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/telemetry` | Ingest a batch of sensor readings (also reachable via IoT Rule → Lambda) |
| `GET` | `/api/v1/wearers/{id}/telemetry?range=24h` | Query recent telemetry for a wearer |
| `POST` | `/api/v1/alerts/{id}/acknowledge` | Acknowledge an alert |
| `POST` | `/api/v1/qr/{wearerId}/rotate` | Rotate a wearer's QR identity token |
| `GET` | `/qr/resolve/{token}` | Public, rate-limited, tiered QR resolution |
| `POST` | `/api/v1/ml/stress-score` | Feature vector → SageMaker invoke → stress score |
| `GET` | `/api/v1/reports/{wearerId}?period=monthly&format=pdf\|csv` | Generate/export reports |

All endpoints use Pydantic request/response models, async handlers, structured JSON logging to CloudWatch, input validation, and API Gateway usage-plan rate limiting.

## Getting Started

### Prerequisites

- Node.js 18+ and npm/pnpm
- Python 3.11+
- Docker (for local DynamoDB via `docker-compose`)
- AWS CLI configured with appropriate credentials
- AWS CDK CLI (`npm install -g aws-cdk`)

### Local Development

```bash
# Clone the repo
git clone https://github.com/<org>/autiguard.git
cd autiguard

# Start local DynamoDB + backend dependencies
docker-compose up -d

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd ../frontend
npm install
npm run dev

# Infrastructure (deploy to AWS)
cd ../infra
npm install
cdk bootstrap
cdk deploy --all
```

## Environment Variables

Backend (`.env` / `pydantic-settings`):

| Variable | Description |
|---|---|
| `COGNITO_USER_POOL_ID` | Cognito User Pool used for JWT verification |
| `DYNAMODB_TABLE` | Single-table DynamoDB table name (`AutiGuardCore`) |
| `KMS_KEY_ID` | KMS key used for QR token signing and field-level encryption |
| `SAGEMAKER_STRESS_ENDPOINT` | SageMaker endpoint name for the stress model |
| `SAGEMAKER_DISTRESS_ENDPOINT` | SageMaker endpoint name for the distress audio model |
| `SNS_TOPIC_ARN` | SNS topic for panic alert fan-out |

> Never commit real values for these — use AWS Secrets Manager / Parameter Store in deployed environments and `.env.local` (gitignored) for local dev.

## Security & Compliance

- TLS 1.2+ in transit; KMS-encrypted at rest (DynamoDB + S3 default encryption).
- Least-privilege IAM roles per Lambda/service — no wildcard policies.
- Field-level KMS envelope encryption for medical notes before persistence.
- AWS WAF on API Gateway/CloudFront, with rate limiting on the public QR-resolve endpoint.
- Immutable audit trail (CloudTrail + `AUDIT#` DynamoDB item pattern) for QR scans, alert acknowledgments, and profile edits.
- Configurable, org-level data retention policy (GDPR/HIPAA-aligned data minimization).

## Non-Functional Targets

- P99 API latency < 300ms for dashboard reads (DAX caching if load testing indicates need).
- WebSocket push latency < 2s from device ping to dashboard update.
- 99.9% uptime target — multi-AZ DynamoDB, Fargate across 2+ AZs.
- Stateless, horizontally scalable FastAPI containers behind ALB/API Gateway, autoscaling on CPU + request count.

## Deployment

- **Infrastructure**: AWS CDK (TypeScript), deployed via `cdk deploy`.
- **Backend**: containerized FastAPI on ECS Fargate (or Lambda via Mangum adapter), fronted by API Gateway.
- **Frontend**: AWS Amplify Hosting or S3 + CloudFront.
- **CI/CD**: GitHub Actions pipeline runs tests, builds artifacts, and triggers CDK/CodeDeploy deployment to staging then production.

## Roadmap / Build Order

1. Scaffold CDK stack: Cognito + DynamoDB table + base API Gateway/Lambda skeleton.
2. Backend: auth guard + wearer CRUD + DynamoDB service layer.
3. Backend: telemetry ingestion + alerts + geofence evaluation Lambda.
4. Backend: QR generation/resolution with KMS signing.
5. Backend: ML proxy endpoints (stubbed behind an interface for local dev).
6. Frontend: auth flow → dashboard shell → live map/vitals → alerts → geofence editor → reports → responder QR view.
7. Wire WebSocket real-time push end-to-end.
8. Security pass: KMS field encryption, WAF rules, IAM least-privilege audit.
9. CI/CD pipeline + staging environment deploy.

## Contributing

1. Fork the repo and create a feature branch.
2. Confirm any DynamoDB schema or API contract changes against `/docs/api-spec.yaml` before implementing frontend components against them.
3. Add/update `pytest` coverage for backend changes.
4. Open a PR describing the change and its impact on the architecture diagram, if any.

---

**Note:** This is a safety-critical application. Any change touching alerting, geofencing, panic escalation, or QR identity resolution should be reviewed with extra care and tested end-to-end before merging.
