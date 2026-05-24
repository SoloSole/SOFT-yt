# Supabase setup

This folder documents the database structure used by the n8n Instagram DM Automation Kit.

The schema is based on a working private implementation, but public examples must use placeholders and safe defaults.

## Quick setup

Run the example schema in your private Supabase SQL editor:

```sql
-- supabase/schema.example.sql
```

Then add your own private account row and keyword flow using your own values. Do not commit private tokens, project URLs, account IDs, or real user data.

## Tables

### `ig_accounts`

Stores connected Instagram professional account metadata.

Important columns:

- `id` - UUID primary key
- `username` - account username
- `ig_user_id` - platform account ID, unique
- `access_token` - private token, keep secret
- `token_expiry` - token expiration timestamp
- `active` - whether the account is active
- `follower_gate_dm` - first button message for gated content
- `follower_check_msg` - message shown when user should follow first
- `follower_success_msg` - message shown after successful check

### `kw_flows`

Stores global keyword rules.

Important columns:

- `id` - UUID primary key
- `account_id` - optional account reference
- `keyword` - trigger keyword
- `match_type` - usually `contains` or `exact`
- `output_type` - usually `url` or `pdf`
- `output_value` - link or content output
- `follower_only` - whether follower gate is required
- `active` - whether the flow is enabled
- `reply_text` - public reply text
- `dm_text` - private message text
- `ig_username` - public username placeholder, for example `your_username`

Keywords are global in the database, not tied to a single post.

### `dm_queue`

Stores pending and processed message jobs.

Important columns:

- `id` - UUID primary key
- `sender_id` - recipient ID from the webhook event
- `comment_id` - source comment ID
- `ig_account_id` - connected account ID
- `dm_text` - message text
- `btn_title` - button label
- `output_value` - destination URL or payload
- `status` - usually `pending` or `sent`
- `created_at` - queue timestamp
- `sent_at` - processed timestamp
- `follower_only` - whether follower gate is required
- `reply_text` - public reply text

### `dm_logs`

Stores delivery and event logs.

Important columns:

- `id` - UUID primary key
- `account_id` - optional account ID
- `ig_user_id` - recipient ID
- `comment_text` - original comment text
- `keyword_matched` - matched keyword
- `output_sent` - sent output value
- `is_follower` - follower check result if used
- `comment_id` - source comment ID
- `created_at` - log timestamp

## Existing indexes

- `dm_logs_pkey` on `dm_logs(id)`
- `dm_queue_pkey` on `dm_queue(id)`
- `ig_accounts_pkey` on `ig_accounts(id)`
- `ig_accounts_ig_user_id_key` on `ig_accounts(ig_user_id)`
- `kw_flows_pkey` on `kw_flows(id)`

## Security note

Keep private credentials outside public SQL examples. Store sensitive values only in your private Supabase project, private n8n credentials, or deployment environment.

Do not publish real:

- access tokens
- service role keys
- account IDs
- project URLs
- production webhook URLs
- private logs

## Files

- `schema.example.sql` - safe example schema with placeholder defaults
