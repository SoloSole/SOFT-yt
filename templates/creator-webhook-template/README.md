# Creator webhook template

This template is the main webhook workflow for Instagram comment-to-message automation.

It is based on a working private workflow, but all private values were removed before publishing.

## What it does

- handles Meta webhook verification
- receives webhook events
- parses comment, postback and message events
- ignores comments created by the connected account itself
- loads the connected account from Supabase
- checks whether the event is a comment or postback
- loads active keyword flows from Supabase
- matches comment text against global keyword rules
- checks for duplicate queue records
- writes a new pending queue record
- logs matched events
- checks follower status for gated postback flows
- sends a follow-up message depending on follower status

## Important setup steps after import

After importing the workflow into n8n:

1. Open every Supabase node
2. Select your own Supabase credential
3. Confirm table names match your Supabase schema
4. Set your webhook path if you do not want to use `instagram-webhook`
5. Configure your Meta Developer webhook URL
6. Activate the workflow only after testing

## Required Supabase tables

- `ig_accounts`
- `kw_flows`
- `dm_queue`
- `dm_logs`

See `../../supabase/schema.example.sql`.

## Where access tokens come from

Do not hardcode account tokens inside the Parse Event node.

The public template expects the account token to be stored in:

```text
ig_accounts.access_token
```

The workflow loads the account by:

```text
ig_accounts.ig_user_id = parsed webhook account ID
```

## Important n8n expression note

Supabase nodes overwrite the current `$json`. After the account lookup, use Parse Event references such as:

```text
$('Parse Event').first().json.eventType
```

instead of:

```text
$json.eventType
```

This applies especially to comment/postback routing and follower checks.

## Own comment protection

Some webhook providers also send events for replies created by the connected account itself.

The parser checks:

```text
senderId === igAccountId
```

and marks the event as:

```text
own_comment
```

This prevents your own public replies from creating another queue record.

## Security checklist

Before making the workflow active:

- no hardcoded access tokens
- no service role keys in Code nodes
- no real account IDs in the public workflow file
- Supabase credentials are stored privately in n8n
- webhook path is configured in Meta Developer
- account rows exist in Supabase
- keyword flows exist and are active

## Testing

Use a test Instagram professional account and a safe test keyword first.

Recommended test flow:

1. Add account to `ig_accounts`
2. Add keyword to `kw_flows`
3. Comment the keyword under a test post
4. Confirm queue row appears in `dm_queue`
5. Confirm log row appears in `dm_logs`
6. Run the queue worker template
