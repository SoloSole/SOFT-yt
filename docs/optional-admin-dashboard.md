# Optional admin dashboard

This project can be extended with a small Next.js dashboard for managing workflow data stored in Supabase.

The dashboard is optional. The n8n workflow templates can work without it if you manage your database rows directly in Supabase.

## Recommended stack

- Next.js
- React
- TypeScript
- Supabase client
- Tailwind CSS or simple CSS
- Environment variables for private configuration

## Suggested pages

### Keyword flows

Purpose: manage keyword-based response rules.

Typical fields:

- keyword
- match type
- output type
- output value
- public response text
- private response text
- account username
- active status

Recommended actions:

- list flows
- create flow
- edit flow
- enable or disable flow
- delete flow

### Accounts

Purpose: manage connected account metadata.

Typical fields:

- username
- platform account ID
- active status
- token expiration date

Do not display full private tokens in the UI. If a token must be shown, mask it heavily or do not render it at all.

### Stats

Purpose: show recent activity and queue health.

Recommended metrics:

- total sent messages
- messages sent today
- pending queue count
- sent count within the last hour
- keyword breakdown
- recent logs

### Debug

Purpose: inspect recent workflow executions during development.

Security warning: this page can expose sensitive runtime data. Do not make it public. Protect it with authentication or disable it in production.

## Environment variables

Use environment variables instead of hardcoded values.

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
N8N_API_URL=https://n8n.yourdomain.com/api/v1
N8N_API_KEY=your-private-n8n-api-key
```

## Security checklist

- never commit `.env.local`
- never hardcode API keys in route files
- never show full tokens in the browser
- keep service role keys server-side only
- protect debug routes
- add authentication before production use
- mask account identifiers where possible
- rotate any secret that was ever pasted into a chat, log, or public file

## Suggested folder structure

```text
admin-dashboard/
├── app/
│   ├── accounts/
│   ├── flows/
│   ├── stats/
│   ├── debug/
│   └── api/
├── lib/
│   └── supabase.ts
├── package.json
└── .env.example
```

## Public release recommendation

Do not publish a production dashboard as-is. First convert it into a clean starter template:

- remove real project branding
- replace all real URLs with placeholders
- move runtime keys to environment variables
- remove hardcoded default account names
- add authentication notes
- replace production table data with examples
