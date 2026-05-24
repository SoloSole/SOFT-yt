# n8n technical notes

These notes document important n8n behavior discovered while building the workflow templates.

## Important notes

1. Supabase nodes overwrite the current `$json` object with database output. After a Supabase account lookup, reference earlier parsed event data with expressions such as:

```text
$('Parse Event').first().json.eventType
```

Do not rely on:

```text
$json.eventType
```

This applies especially to routing and follow-up checks.

2. Some platforms may send webhook events for replies created by your own account. The parser should detect when the sender is the same as the connected account and mark it as an internal comment event. That event should not be added to the queue.

3. Queue workers should use conservative batch sizes and should mark records as processed only after successful delivery or after a controlled failure path.

## Workflow routing notes

- Comment check nodes should read `eventType` from `$('Parse Event').first().json.eventType`.
- Postback check nodes should read `eventType` from `$('Parse Event').first().json.eventType`.
- Follow-up API calls should read `senderId` and runtime token values from `$('Parse Event').first().json` when needed.

## Common problems

| Problem | Cause | Fix |
|---|---|---|
| eventType is undefined after account lookup | The database node overwrote `$json` | Use `$('Parse Event').first().json.eventType` |
| Follow-up request has an invalid token | Runtime data was overwritten by account lookup output | Use the parsed event data reference instead of `$json` |
| Own reply triggers the workflow again | The platform sends webhooks for replies created by the same account | Detect sender/account equality and ignore the event |
| Queue keeps retrying old broken rows | Old queue records have invalid recipient data | Clear or mark old pending rows after verifying they are safe to skip |
