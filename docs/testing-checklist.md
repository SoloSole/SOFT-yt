# Testing checklist

Use this checklist after importing the workflow templates and creating the Supabase tables.

The goal is to test the full flow safely before turning on production automation.

## 1. Database check

Confirm that these tables exist in Supabase:

- `ig_accounts`
- `kw_flows`
- `dm_queue`
- `dm_logs`

Confirm that `ig_accounts` has one active test account row.

Confirm that `kw_flows` has one active keyword flow.

## 2. Credential check

In n8n, open every Supabase node and select your own Supabase credential.

Check that no node contains public or hardcoded private values.

Do not hardcode private keys or account tokens in Code nodes.

## 3. Webhook verification check

In Meta Developer settings, configure the webhook URL from your active n8n workflow.

Expected result:

- Meta sends a challenge request
- n8n receives it
- `Respond Challenge` returns the challenge value
- webhook verification passes

## 4. Comment event check

Post a test comment with your configured keyword.

Expected result:

- `Webhook Events (POST)` runs
- `Parse Event` returns `eventType = comment`
- `Get Account` finds the connected account
- `Is Comment?` routes to the keyword flow branch
- `Get KW Flows` returns active flows
- `Match KW` finds the keyword

## 5. Queue check

After a matched comment, check Supabase.

Expected result in `dm_queue`:

- one new row
- `status = pending`
- correct `sender_id`
- correct `comment_id`
- correct `ig_account_id`
- expected `dm_text`
- expected `output_value`

## 6. Duplicate check

Comment the same keyword again in a way that reuses the same comment event or replay the same test event.

Expected result:

- duplicate queue row should not be created for the same `comment_id`

## 7. Queue worker check

Run the queue worker manually before activating its schedule.

Expected result:

- worker counts recent sent rows
- worker calculates batch size
- worker loads pending rows
- worker sends the private message
- worker posts public reply if configured
- worker updates the row to `status = sent`
- `sent_at` is set

## 8. Log check

Check `dm_logs`.

Expected result:

- matched keyword is logged
- output value is logged
- source comment ID is logged
- timestamp exists

## 9. Follower gate check

For flows using follower-only logic, test both cases:

- user follows the account
- user does not follow the account

Expected result:

- followers receive the content link
- non-followers receive the follow/check-again message

## 10. Own comment protection check

When the automation posts a public reply, confirm it does not trigger a new queue record.

Expected result:

- `Parse Event` detects the connected account as the sender
- event is marked as an own comment
- no new queue row is created

## 11. Rate limit check

Confirm that the queue worker uses conservative defaults:

- 180 messages per hour
- maximum 6 records per run
- scheduled interval of 2 minutes

Adjust only if you understand the platform limits and risks.

## 12. Production readiness check

Before enabling production use:

- rotate any secret that was pasted into chats, logs, screenshots, or files
- confirm all real tokens are private
- confirm `.env` files are not committed
- confirm dashboard routes are protected
- confirm debug pages are disabled or private
- test with a low-volume account first
- monitor failed executions

## Common fixes

| Problem | Likely cause | Fix |
|---|---|---|
| `eventType` is undefined | Supabase node overwrote `$json` | Use `$('Parse Event').first().json.eventType` |
| No account is found | `ig_accounts.ig_user_id` does not match webhook account ID | Check account row |
| No keyword is matched | keyword inactive or match type mismatch | Check `kw_flows` |
| Queue row is not created | duplicate check or IF condition blocked it | Check `comment_id` and matched output |
| Worker sends nothing | no pending rows or batch size is zero | Check `dm_queue` and recent sent count |
| Row stays pending | update filter did not match row ID | Check Mark as Sent node |
