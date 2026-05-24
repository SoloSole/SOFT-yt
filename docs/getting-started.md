# Getting started

This guide explains the high-level setup for using the templates in this repository.

## Requirements

- n8n Cloud or self-hosted n8n
- Supabase project
- Meta Developer app
- Instagram professional account connected to Meta
- Public HTTPS webhook URL
- Basic understanding of API credentials and environment variables

## Setup overview

1. Create a Supabase project
2. Run the SQL schema from `supabase/schema.sql`
3. Create a Meta Developer app
4. Configure Instagram permissions and webhook fields
5. Import the n8n workflow template
6. Replace placeholder values with your own credentials
7. Activate the workflow
8. Test with a real Instagram comment keyword

## Recommended production setup

For production use, run n8n behind HTTPS on a custom domain. A VPS with Docker and a reverse proxy is enough for many small projects.

Do not expose internal admin tools without authentication.

## Placeholders

All examples use placeholder values. Replace them with your own values in your private n8n instance, not in this public repository.
