# Worked examples

Two fictional tickets, one per shape. Match their density and tone. The
project key `PROJ`, the repos, and the services are invented.

## Feature ticket: PROJ-412 (child of a product epic)

Summary: `[Backend] M1: Inventory: expire reservations after a TTL, release stock, publish ReservationReleased, update the reservations runbook`

```
**Acceptance Criteria**

* A reservation created with no `ttl_seconds` gets the tenant default (900) and has `expires_at` set on the row.
* The sweeper releases a reservation created with `ttl_seconds=60` within one sweep interval after `expires_at`, and the SKU's (stock keeping unit) `available` count rises by the reserved quantity.
* Each release publishes one `ReservationReleased` with `reservation_id`, `sku`, `quantity`, `reason=EXPIRED`.
* The sweeper never releases a reservation confirmed before `expires_at`, and publishes no event for it.
* Two sweeper pods running at once release each expired reservation exactly once.
* `ReservationService` rejects `ttl_seconds` above the tenant maximum (86400) with 400 `ttl_too_long`.
* `inventory.reservation_released` increments once per release, tagged `reason`, `tenant_tier`.
* The reservations runbook has an "expired reservations" section.

**Description**

Give each reservation a TTL (time to live) so abandoned carts stop holding stock. Spec: <wiki url> (sections 2 and 4, M1 row "expiry, sweeper").

**Blocked by** PROJ-402, the schema change that adds `expires_at` and `released_reason` to `inventory_reservations` (linked).

**Clock.** The sweeper compares `expires_at` to database time, not pod time, so clock drift between pods cannot release early. `ReservationService` writes `expires_at` once at create and never extends it; extension is M2.

**Idempotency.** Release is a conditional update (`status = ACTIVE AND expires_at <= now()`), so a second sweeper or a concurrent confirm loses the race cleanly. Only the pod whose update changed the row publishes the event.

**Capacity caveat.** The sweeper runs on every pod with no leader election. Each sweep claims at most 500 rows, so a backlog after an outage drains at 500 per interval per pod. The metrics ticket alerts on backlog age.

The checkout consumer deserializes with unknown properties ignored and reacts only to `reason`, so existing `CANCELLED` releases are untouched by construction.

**Technical Notes**

Repo: inventory-service.

* `model/Reservation.java`: add `expiresAt` and `releasedReason`. `expiresAt = created + ttl`.
* `service/ReservationService.java` `create`: default `ttlSeconds` from `TenantLimits`; reject above the maximum with 400 `ttl_too_long`; set `expiresAt`. `confirm`: use the same conditional-update guard so it cannot confirm a row the sweeper already released.
* `job/ReservationSweeper.java` (new). Every `sweep.interval` (default 30s):
    1. `UPDATE inventory_reservations SET status = RELEASED, released_reason = EXPIRED WHERE status = ACTIVE AND expires_at <= now() LIMIT 500`, returning the claimed ids.
    2. For each claimed id, add `quantity` back to `sku_stock.available` in the same transaction.
    3. Commit, then publish one `ReservationReleased` per claimed id.
    4. If 500 rows were claimed, run again immediately; otherwise wait for the interval.
* Guards:
    * Publish after commit, not inside the transaction, so a bus outage does not roll back a release. A release without an event is recoverable from `released_reason`; the reverse is not.
    * `now()` is the database clock. Do not pass a pod timestamp into the query.
    * Rows with `expires_at` null (created before the migration) are never swept. M2 backfills them.
* `realtime/ReservationEventPublisher.java`: new `ReservationReleased` message. The serializer and topic config are reused unchanged.
* Metric: counter `inventory.reservation_released` tagged `reason` (EXPIRED / CANCELLED), `tenant_tier`. No tenant id tag.
* Docs: add an "expired reservations" section to the reservations runbook.
* A working commit exists on the local branch `PROJ-400-reservation-ttl` (not pushed); rename the branch to this ticket's key before opening the PR.
```

## Hygiene ticket: PROJ-431 (child of the internal-improvements epic)

Summary: `[Backend] Remove unused direct dependencies from billing-worker`

```
Remove direct dependencies that `worker/pom.xml` declares but no source file uses. `mvn dependency:analyze` reports each one as an unused declared dependency, and no `import` references them in `src/`. An earlier XML report format and the AWS SDK v1 SQS (Simple Queue Service) client added them. The AWS SDK v2 migration (PR #212) made the SQS and JAXB (Java Architecture for XML Binding) set obsolete.

**Acceptance Criteria**

* `worker/pom.xml` no longer declares `com.fasterxml.jackson.dataformat:jackson-dataformat-xml`, `org.glassfish.jaxb:jaxb-runtime`, `javax.annotation:javax.annotation-api`, `org.apache.commons:commons-text`, or `com.amazonaws:aws-java-sdk-sqs`.
* `worker/pom.xml` no longer defines the `jaxb.version` property.
* The service starts and the integration tests pass.
* The version is 3.5.0 (minor bump from 3.4.0).

**Technical Notes**

* Repo: `billing-worker`, file `worker/pom.xml`.
* PR: <pull request url>
* Leave `config-core`, `bus-client`, and `metrics-shim` in place. The analyzer flags them, but they are loaded reflectively through config.
* `jersey-client` 2.35 still pulls `javax.annotation-api` 1.3.2 transitively. That is expected.
```

A smaller one, PROJ-428, shows the minimum:

```
Update low-risk pinned packages in `requirements.txt` to the latest minor or patch release. Do not change any major version.

**Acceptance Criteria**

* requests, pyyaml, click, and attrs use the latest minor or patch release.
* CI passes.

**Technical Notes**

* PR: <pull request url>
* Review the auth client first. It moves from 2.4 to 2.6.
```
