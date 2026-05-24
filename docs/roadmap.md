# Roadmap

This roadmap describes the planned public development of the n8n Instagram DM Automation Kit.

## v0.1.0 - Public foundation

Goal: make the project understandable and safe to inspect publicly.

- publish project README
- document architecture
- document Supabase table structure
- add security and secret handling guide
- add optional dashboard notes
- add setup guide
- add environment variable example
- add MIT license

## v0.2.0 - Workflow templates

Goal: publish clean n8n workflow exports that can be imported safely.

- add sanitized webhook workflow template
- add sanitized queue worker workflow template
- remove all private account identifiers
- replace all private values with placeholders
- add import instructions
- add testing checklist
- add troubleshooting notes for common n8n expression issues

## v0.3.0 - Database examples

Goal: make Supabase setup easier for new users.

- add `schema.example.sql`
- add `seed.example.sql`
- add safe sample keyword flows
- add recommended indexes
- add row-level security notes
- add service role warning

## v0.4.0 - Optional admin dashboard starter

Goal: provide a clean starter dashboard without production secrets.

- extract dashboard into a generic starter template
- remove project-specific branding
- move API URLs and keys to environment variables
- add `.env.example`
- add basic authentication notes
- mask sensitive account/token values in UI
- document deployment options

## v0.5.0 - Deployment guide

Goal: help users self-host the project.

- add Docker-based n8n deployment notes
- add reverse proxy notes
- add custom domain and HTTPS notes
- add Cloudflare-style DNS notes
- add backup notes for Supabase and n8n
- add production hardening checklist

## Future ideas

- multi-account management guide
- webhook verification helper
- safer token rotation workflow
- screenshots and demo GIFs
- example dashboard screenshots with fake data
- issue templates and pull request templates
- community workflow submissions

## Project principles

- keep examples safe and free of secrets
- prefer clear documentation over magic
- respect platform rules and rate limits
- make workflows understandable for builders
- keep the system self-hostable and transparent
