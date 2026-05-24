# Architecture

The first toolkit focuses on a self-hosted Instagram comment-to-DM flow.

## High-level flow

```text
Instagram comment
      ↓
Meta webhook
      ↓
n8n webhook workflow
      ↓
Supabase keyword lookup
      ↓
Queue table
      ↓
Queue worker workflow
      ↓
Instagram message API
      ↓
Supabase logs
```

## Components

### n8n

n8n receives webhook events, parses them, checks keywords, writes queue records, sends messages, and logs results.

### Supabase

Supabase stores account metadata, keyword flows, queued messages, and delivery logs.

### Meta Developer app

A Meta app provides Instagram permissions, webhook subscriptions, and access tokens.

### Optional admin dashboard

An external dashboard can be built on top of Supabase to manage keyword flows, accounts, logs, and queue status.

## Self-hosted deployment

A common setup is:

```text
Internet
  ↓
Cloudflare or DNS provider
  ↓
HTTPS reverse proxy
  ↓
self-hosted n8n
  ↓
Supabase and Meta APIs
```

## Rate limiting

This project should not send messages without limits. Use a queue worker and conservative batch size. Platform limits and account quality rules still apply.
