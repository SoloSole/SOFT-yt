# Security Policy

## Do not commit secrets

Never commit real production secrets to this repository.

Do not publish:

- API keys
- access tokens
- service role keys
- webhook verify tokens
- private webhook URLs
- internal domains or IP addresses
- personal emails
- database credentials
- account identifiers
- production logs containing private data

Use placeholders such as:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
META_VERIFY_TOKEN=your-random-verify-token
INSTAGRAM_ACCESS_TOKEN=your-long-lived-token
N8N_PUBLIC_URL=https://n8n.yourdomain.com
```

## Before publishing workflow exports

n8n workflow exports should be reviewed manually before being added to this repository. Replace all private values with placeholders and remove any production-only credentials.

## Responsible use

Users are responsible for complying with Meta Platform rules, Instagram policies, privacy laws, and local regulations. This project does not bypass platform rules or rate limits.
