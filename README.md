# n8n Creator Automation Kit

Open-source n8n workflow templates for creators, marketers, indie builders, and small teams.

The first module is a self-hosted Instagram comment-to-DM automation toolkit powered by n8n, Supabase, Meta Developer APIs, and an optional admin dashboard.

It is designed as a practical open-source alternative to hosted social automation tools: you run your own infrastructure, keep your own database, and avoid artificial monthly message caps from this project. Meta/Instagram API limits, permissions, messaging rules, and platform policies still apply.

## What this project is

This project provides documented n8n workflow templates for creator and marketing automations, starting with Instagram keyword-comment-to-DM workflows.

The main idea is simple:

- users comment a keyword under a post
- Meta sends a webhook event
- n8n receives and parses the event
- Supabase stores keyword rules, connected accounts, queue records, and logs
- a queue worker sends the follow-up message safely with rate limiting
- an optional dashboard lets you manage keywords, texts, accounts, queue status, and logs

## Current focus: Instagram comment-to-DM automation

```text
Instagram comment with keyword
        ↓
Meta Webhook
        ↓
n8n workflow
        ↓
Supabase keyword lookup
        ↓
DM queue / rate limit layer
        ↓
Instagram message with button or link
        ↓
Logs and stats
```

## Keyword logic

Keywords are stored globally in the database, not per post.

That means a creator can write something like `comment "guide" below` in a post, but the workflow will match any active keyword that exists in the database. If a different active keyword is commented, the user receives the content configured for that keyword.

This keeps the system simple, reusable, and easy to manage from the database or optional dashboard.

## Why self-host this?

Hosted automation tools are convenient, but they can become expensive or limited as usage grows. A self-hosted stack gives you more control over workflows, data, custom logic, and the number of connected accounts.

Typical costs are your own infrastructure costs such as a VPS, database, and domain. Platform limits still apply, especially Meta/Instagram rate limits and messaging policies.

## Planned templates

- Instagram comment keyword → message automation
- queue worker with rate limiting
- Supabase-backed keyword flow management
- optional follower-gate style postback flow
- optional admin dashboard integration notes
- self-hosted n8n + Cloudflare + VPS deployment notes

## Repository structure

```text
.
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── docs/
│   ├── getting-started.md
│   ├── architecture.md
│   ├── optional-admin-dashboard.md
│   ├── n8n-technical-notes.md
│   └── security-and-secrets.md
├── examples/
│   └── .env.example
├── supabase/
│   └── README.md
└── templates/
    └── creator-webhook-template/
        └── workflow.json
```

## Important security note

This repository never includes real production tokens, webhook verify tokens, access tokens, private domains, account IDs, internal IPs, emails, or database service keys. All sensitive values must be replaced with placeholders before publishing.

See [`docs/security-and-secrets.md`](docs/security-and-secrets.md).

## Status

Early public setup. Workflow templates are being sanitized and documented before publication.

## License

MIT License.
