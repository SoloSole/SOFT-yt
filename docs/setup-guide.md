# Setup guide

This guide explains the planned setup flow for the n8n Instagram DM Automation Kit.

The project is designed for builders who want to run their own Instagram comment-to-message automation stack with n8n, Supabase, Meta Developer APIs, and optional dashboard tooling.

## Before you start

You need:

- an Instagram professional account
- a Meta Developer account
- a Meta app with the required Instagram permissions
- n8n Cloud or self-hosted n8n
- a Supabase project
- a public HTTPS webhook URL
- basic knowledge of credentials and environment variables

## 1. Create a Supabase project

Create a new Supabase project and keep the project URL and keys private.

You will use Supabase to store:

- connected account metadata
- keyword rules
- pending queue records
- delivery logs

Do not publish your Supabase URL, anon key, or service role key in a public repository.

## 2. Create the database tables

Create the tables documented in `supabase/README.md`:

- `ig_accounts`
- `kw_flows`
- `dm_queue`
- `dm_logs`

A clean SQL example will be added later as `supabase/schema.example.sql`.

## 3. Create a Meta Developer app

Create a Meta app and connect your Instagram professional account.

You will need webhook access and Instagram messaging/comment permissions supported by your app setup.

Keep all app IDs, verify tokens, account IDs, and access tokens private.

## 4. Configure a webhook URL

Your n8n instance must expose a public HTTPS webhook URL, for example:

```text
https://n8n.yourdomain.com/webhook/instagram-webhook
```

Use your own verify token and store it privately.

## 5. Import the n8n workflows

The project is planned to include two main workflow templates:

- webhook workflow: receives and parses events, matches keywords, and writes queue records
- queue worker workflow: processes pending records with a conservative rate limit

Before importing any workflow JSON, review it for placeholders and replace them only inside your private n8n instance.

## 6. Configure n8n credentials

Create credentials for:

- Supabase
- Meta / Instagram API requests
- any optional private dashboard or API access

Avoid hardcoding tokens in Code nodes. Prefer n8n credentials or private environment variables where possible.

## 7. Add your first account

Insert your connected account into `ig_accounts`.

Use your own values for:

- username
- platform account ID
- private token
- token expiry
- active status
- default response texts

## 8. Add your first keyword flow

Insert a row into `kw_flows`.

Example concept:

```text
keyword: guide
match_type: contains
output_type: url
output_value: https://yourdomain.com/guide
reply_text: Sending it to you now.
dm_text: Here is your link.
active: true
```

Keywords are global in the database, not tied to a single post.

## 9. Test the flow

Test with a real post and a real comment keyword.

Recommended checks:

- webhook receives the event
- parser detects the event type
- keyword is matched
- queue record is created
- queue worker sends the message
- log record is created
- public reply works if enabled

## 10. Use the optional dashboard

The optional dashboard can make management easier by allowing you to manage:

- keyword flows
- message texts
- connected accounts
- queue status
- logs and statistics

Do not expose the dashboard publicly without authentication.

## Troubleshooting

See:

- `docs/n8n-technical-notes.md`
- `docs/security-and-secrets.md`
- `docs/optional-admin-dashboard.md`

## Security reminder

Never publish real tokens, service keys, webhook URLs, account IDs, internal domains, or private logs.
