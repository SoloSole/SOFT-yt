# n8n Creator Automation Kit

Open-source n8n workflow templates for creators, marketers, indie builders, and small teams.

This repository is being built as a practical self-hosted alternative to hosted Instagram DM automation tools. The first toolkit focuses on Instagram keyword-comment-to-DM flows powered by n8n, Supabase, Meta Developer APIs, and optional self-hosted admin dashboards.

## What this project is

This project provides documented n8n automation templates for common creator and marketing workflows, starting with Instagram comment-to-DM automation.

The goal is to help builders run their own automation stack instead of depending entirely on paid platforms with monthly message limits. You still need to follow Meta Platform rules, Instagram API limits, messaging windows, and applicable privacy laws.

## Current focus: Instagram DM automation

The first planned template is a self-hosted Instagram automation flow:

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
Instagram DM with button or link
        ↓
Logs and stats
```

## Why self-host this?

Hosted automation tools are convenient, but they can become expensive or limited as usage grows. A self-hosted stack gives you more control over workflows, data, custom logic, and the number of connected accounts.

Typical costs are your own infrastructure costs such as a VPS, database, and domain. Platform limits still apply, especially Meta/Instagram rate limits and messaging policies.

## Planned templates

- Instagram comment keyword → DM automation
- DM queue worker with rate limiting
- Supabase-backed keyword flow management
- Optional follower-gate style postback flow
- Admin dashboard integration notes
- Self-hosted n8n + Cloudflare + VPS deployment notes

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
│   ├── self-hosted-n8n.md
│   ├── meta-developer-setup.md
│   ├── supabase-setup.md
│   └── security-and-secrets.md
├── examples/
│   └── .env.example
├── supabase/
│   ├── schema.sql
│   ├── grants.sql
│   └── seed.example.sql
└── templates/
    ├── instagram-comment-to-dm/
    │   ├── README.md
    │   ├── setup.md
    │   └── workflow.json
    └── instagram-dm-queue-worker/
        ├── README.md
        ├── setup.md
        └── workflow.json
```

## Important security note

This repository never includes real production tokens, webhook verify tokens, access tokens, private domains, account IDs, internal IPs, emails, or database service keys. All sensitive values must be replaced with placeholders before publishing.

See [`docs/security-and-secrets.md`](docs/security-and-secrets.md).

## Status

Early public setup. Workflow templates are being sanitized and documented before publication.

## License

MIT License.