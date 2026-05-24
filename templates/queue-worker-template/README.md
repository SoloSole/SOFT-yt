# Queue worker template

This template processes pending records from the `dm_queue` table.

It is based on a working private workflow, but all private values were removed before publishing.

## What it does

- runs on a schedule
- counts messages sent during the last 60 minutes
- calculates a conservative batch size
- loads pending queue records
- sends the configured follow-up message
- optionally posts a public reply after the private message succeeds
- marks queue records as sent

## Default rate limit logic

The template uses conservative default values:

```text
hourly limit: 180
max batch size: 6
schedule interval: every 2 minutes
```

These values are intentionally conservative. You are responsible for respecting Meta/Instagram limits, account quality rules, messaging windows, and platform policies.

## Required Supabase table

The worker reads and updates:

```text
dm_queue
```

Expected fields include:

- `id`
- `sender_id`
- `comment_id`
- `ig_account_id`
- `access_token`
- `dm_text`
- `btn_title`
- `output_value`
- `status`
- `sent_at`
- `follower_only`
- `reply_text`

See `../../supabase/schema.example.sql`.

## Important setup steps after import

After importing the workflow into n8n:

1. Open every Supabase node
2. Select your own Supabase credential
3. Confirm the `dm_queue` table exists
4. Confirm the queue rows contain valid account and recipient values
5. Test with one pending record before activating the schedule
6. Keep the workflow inactive until your test succeeds

## Public reply behavior

The worker can post a public reply after the private message step succeeds.

This order is intentional:

```text
private message first
public reply second
mark queue record as sent third
```

That avoids publicly saying that a message was sent when the private message failed.

## Common problems

| Problem | Likely cause | Fix |
|---|---|---|
| No pending records are processed | `dm_queue.status` is not `pending` | Check queue rows |
| Batch size is zero | Hourly limit has been reached | Wait or increase only if safe |
| Message request fails | Invalid token or recipient ID | Check account token and queue data |
| Public reply fails | Old or invalid comment ID | Keep failure handling enabled |
| Rows repeat forever | Record was not marked as sent | Check update node filters |

## Security checklist

- keep account tokens private
- do not commit real queue rows
- do not publish production recipient IDs
- review failed executions for sensitive data before sharing logs
- use your own n8n credentials after import
