# Tech brief: Inventory reservation expiry (M1)

## 1. Goal

A reservation holds stock for a cart. Today it holds it forever if the
shopper walks away. Give each reservation a time to live, release the
stock when it lapses, and tell checkout about it.

## 2. Storage

Add `expires_at DATETIME NULL` and `released_reason VARCHAR(16) NULL` to
`inventory_reservations`. `expires_at = created + ttl`. The tenant default
TTL is 900 seconds; the tenant maximum is 86400. Owned by the schema change
ticket, already filed.

## 3. Sweeper

A job on every pod claims expired rows with a conditional update
(`status = ACTIVE AND expires_at <= now()`), returns the quantity to
`sku_stock.available`, and publishes one `ReservationReleased` per row.
Compare against database time. No leader election; claim at most 500 rows
per sweep.

## 4. Event

`ReservationReleased` carries `reservation_id`, `sku`, `quantity`,
`reason` (`EXPIRED` or `CANCELLED`). Checkout reacts only to `reason`.

## 5. API

`POST /reservations` accepts optional `ttl_seconds`. When omitted, the
service applies the tenant default of 1800 seconds. Values above the
tenant maximum return 400 `ttl_too_long`.

## 6. Metric

Counter `inventory.reservation_released` tagged `reason`, `tenant_tier`.

## 7. Milestones

M1: storage, sweeper, event, metric. M2: TTL extension and backfill of
pre-migration rows.
