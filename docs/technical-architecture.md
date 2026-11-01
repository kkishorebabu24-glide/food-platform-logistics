# Technical Architecture

## 1. Purpose

This logistics platform coordinates the flow of food orders across a residential community. The system must handle many buyers, many sellers, shared time windows, queue-based fulfillment, and pickup verification in a secure and measurable way.

## 2. Design Principles

- Local fulfillment, not generic delivery: sellers are micro-fulfillment centers
- State-driven operations: orders and batches move through validated state transitions
- Event-driven architecture: operational signals are captured as events
- Capacity-aware scheduling: each seller has operational limits
- Security-first access model: every action is role-scoped and auditable
- Data-driven operations: dashboards, alerts, and forecasts are built from event telemetry

## 3. Operating Model

### 3.1 Actors

- Buyer: places food orders and picks them up
- Seller: prepares meals and manages fulfillment
- Admin: monitors platform, resolves issues, enforces trust policies
- Logistics system: orchestrates order flow, queue, capacity, pickup, and operational intelligence

### 3.2 Real workflows

1. buyer places order
2. order is validated against seller capacity and slot availability
3. seller accepts or rejects
4. seller prepares order in a batch window
5. order is marked ready for pickup
6. buyer verifies identity / pickup token
7. order is marked picked up or escalated to exception flow

## 4. High-Level Architecture

### 4.1 Layers

- Presentation layer: buyer, seller, and admin experiences
- API layer: REST endpoints for order, fulfillment, pickup, admin, and metrics
- Domain layer: order lifecycle, queue policy, fulfillment logic, exception rules
- Integration layer: notifications, payments, admin systems, analytics ingestion
- Data layer: transactional DB, cache/queue, analytics warehouse
- Observability layer: logs, traces, metrics, alerts, dashboards

## 5. Core Domain Components

### 5.1 Order Service

Responsibilities:

- create and validate order requests
- check seller availability and slot capacity
- enforce pricing and payment rules
- update state transitions
- emit order events

### 5.2 Seller Queue Service

Responsibilities:

- maintain backlog per seller
- determine accepted, preparing, ready, delayed, and failed orders
- evaluate queue pressure and capacity thresholds
- route delays or cancellation reasons

### 5.3 Batch Service

Responsibilities:

- group orders into seller batches
- align orders to a prep window
- determine readiness time and pickup schedule
- track batch health and exception status

### 5.4 Pickup Verification Service

Responsibilities:

- validate buyer identity and order match
- enforce pickup windows and verification token rules
- track no-show and failed verification events
- escalate disputes and mismatches

### 5.5 Exception Service

Responsibilities:

- detect late orders, missing pickups, mismatches, or seller failures
- create exception case records
- trigger refund or admin escalation flows
- populate operational insights and risk models

### 5.6 Analytics Service

Responsibilities:

- aggregate order, batch, and pickup events
- compute seller and buyer performance metrics
- expose dashboards and operational KPIs
- enable forecasting and risk detection

## 6. Event Model

Every significant action emits an event. Event streams are used for operational logic and analytics.

Example event types:

- order.created
- order.validated
- order.accepted
- order.rejected
- order.preparing
- batch.ready_for_pickup
- pickup.verified
- pickup.failed
- order.cancelled
- exception.created
- refund.initiated
- admin.action.approved

Required event payload:

- event_id
- entity_type
- entity_id
- actor_id
- actor_role
- timestamp
- source
- reason_code
- metadata

## 7. State Model

### Order states

- CREATED
- VALIDATED
- ACCEPTED
- REJECTED
- PREPARING
- READY_FOR_PICKUP
- PICKUP_VERIFICATION_PENDING
- PICKED_UP
- COMPLETED
- CANCELLED
- DELAYED
- FAILED
- REFUND_PENDING
- REFUNDED

### Batch states

- BATCH_CREATED
- PREPARATION_IN_PROGRESS
- READY_FOR_PICKUP
- PICKUP_WINDOW_OPEN
- BATCH_CLOSED
- BATCH_EXCEPTION

Server-side validation should enforce legal transitions. No client should directly control lifecycle progression.

## 8. Data Architecture

### 8.1 Transactional database

Use PostgreSQL for operational records:

- users and roles
- sellers and profiles
- residents and trust metadata
- menus and menu items
- orders and order items
- batches and queue positions
- pickup sessions
- payment and refund records
- audit logs
- exception cases

### 8.2 Cache and queue

Use Redis for:

- session management
- order queue snapshots
- short-lived cache
- rate limiting
- background job coordination
- real-time state lookups

### 8.3 Analytics warehouse

Use a warehouse or analytical store for:

- seller throughput
- order completion rates
- no-show and delay trends
- pickup performance
- throughput by time slot
- risk and anomaly detection

## 9. Operational Telemetry and Sensing

The system needs end-to-end operational visibility.

### 9.1 Application sensing

Collect event telemetry from:

- order submission
- menu interaction
- seller acceptance
- status changes
- pickup verification flows
- notification delivery
- admin overrides

### 9.2 Seller and queue sensing

Track:

- active queue counts
- prep duration
- order acceptance rate
- delays and causes
- batch completion metrics
- peak usage by meal window

### 9.3 Pickup sensing

Track:

- pickup window adherence
- verification method used
- failed verification attempts
- no-show events
- mismatched order or identity events

### 9.4 Infra monitoring

Use:

- Prometheus for metrics
- Grafana for dashboards
- OpenTelemetry for tracing
- centralized structured logs
- alerting on anomalies and failures

## 10. Security Architecture

### 10.1 Identity and access

- strong authentication with role-based access control
- admin privileges restricted and monitored
- session enforcement and token rotation
- least privilege for service accounts

### 10.2 Data protection

- TLS for all app and API traffic
- encrypted storage for sensitive fields
- secret management for environment variables and keys
- masked logs for OTPs, tokens, and user-identifying data

### 10.3 Abuse protection

- rate limiting on public endpoints
- suspicious activity detection
- repeated failed verification detection
- bot and abuse monitoring

### 10.4 Auditability

Each action must produce an auditable record:

- actor
- timestamp
- action
- affected entity
- reason or policy trigger
- source device or session

## 11. Recommended Stack

- Backend: FastAPI
- DB: PostgreSQL
- Cache/queue: Redis
- Event bus: Kafka or RabbitMQ
- Analytics: ClickHouse / BigQuery / Snowflake
- Monitoring: Prometheus + Grafana + OpenTelemetry
- Notifications: email, SMS, WhatsApp gateway
- Deployment: Docker / Docker Compose, production via Kubernetes if needed

## 12. Deployment Views

### Local development

- app service
- PostgreSQL
- Redis
- message broker
- monitoring stack

### Production

- multiple application instances
- managed PostgreSQL cluster or RDS equivalent
- managed Redis
- broker cluster
- metrics and log aggregation
- backup and disaster recovery pipeline

## 13. Risks and Mitigations

### Risk: overloading a seller
Mitigation: capacity windows, queue pressure checks, batch staging, delay detection.

### Risk: pickup confusion or identity mismatch
Mitigation: verification token, admin escalation, audit logs, geofencing if needed.

### Risk: data leakage
Mitigation: strict RBAC, masking, encrypted storage, monitoring, access reviews.

### Risk: operational blind spots
Mitigation: event-driven telemetry, dashboards, anomaly alerts, reporting.

## 14. Summary

The logistics system is the operational brain of the food platform. It gives the product a structured way to coordinate demand, seller capacity, pickup events, and operational decisions across a society environment while preserving trust, security, and measurable performance.
