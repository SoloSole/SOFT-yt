# Security and secrets

This project is designed to be public. That means every workflow, SQL file, and example must be safe to share.

## Never publish

- real access tokens
- API keys
- Supabase service role keys
- webhook verify tokens
- real webhook URLs
- private domains or subdomains
- internal server IP addresses
- production usernames
- real Instagram account IDs
- personal emails
- logs with user data

## Use placeholders

Use values like:

```text
YOUR_N8N_WEBHOOK_URL
YOUR_SUPABASE_URL
YOUR_SUPABASE_SERVICE_ROLE_KEY
YOUR_META_VERIFY_TOKEN
YOUR_INSTAGRAM_ACCESS_TOKEN
YOUR_IG_ACCOUNT_ID
YOUR_ADMIN_DASHBOARD_URL
```

## n8n export checklist

Before publishing a workflow export:

- search for `token`
- search for `secret`
- search for `key`
- search for `Authorization`
- search for `Bearer`
- search for real domains
- search for real emails
- search for account IDs
- replace production URLs with placeholders
- remove credentials references if they reveal private names

## Recommended secret storage

Keep secrets in your private n8n credentials, environment variables, or private deployment config. Do not hardcode them in public workflow exports.
