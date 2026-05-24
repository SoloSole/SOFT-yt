-- Example Supabase schema for n8n Instagram DM Automation Kit
-- Review before production use. Do not commit real secrets or production data.

create extension if not exists pgcrypto;

create table if not exists public.ig_accounts (
  id uuid primary key default gen_random_uuid(),
  username text not null,
  ig_user_id text not null unique,
  access_token text not null,
  token_expiry timestamp with time zone,
  active boolean default true,
  created_at timestamp with time zone default now(),
  welcome_dm_text text default 'Hey! Thanks for following!',
  first_contact_dm text default 'Hey! Thanks for reaching out!',
  follower_gate_dm text default 'Get content',
  follower_check_msg text default 'This content is for followers only. Follow and click again.',
  follower_success_msg text default 'Here is your content.'
);

create table if not exists public.kw_flows (
  id uuid primary key default gen_random_uuid(),
  account_id uuid references public.ig_accounts(id) on delete cascade,
  keyword text not null,
  match_type text default 'contains',
  output_type text not null,
  output_value text not null,
  follower_only boolean default true,
  non_follower_msg text default 'This content is for followers only. Follow and try again.',
  active boolean default true,
  created_at timestamp with time zone default now(),
  reply_text text default 'Sending it to your inbox.',
  dm_text text default 'Here is your content.',
  ig_username text default 'your_username'
);

create table if not exists public.dm_queue (
  id uuid primary key default gen_random_uuid(),
  sender_id text not null,
  comment_id text not null,
  ig_account_id text not null,
  access_token text,
  dm_text text not null,
  btn_title text not null,
  output_value text not null,
  status text default 'pending',
  created_at timestamp with time zone default now(),
  sent_at timestamp with time zone,
  follower_only boolean default false,
  reply_text text
);

create table if not exists public.dm_logs (
  id uuid primary key default gen_random_uuid(),
  account_id uuid references public.ig_accounts(id) on delete set null,
  ig_user_id text,
  comment_text text,
  keyword_matched text,
  output_sent text,
  is_follower boolean,
  created_at timestamp with time zone default now(),
  comment_id text
);

create index if not exists dm_queue_status_created_at_idx on public.dm_queue(status, created_at);
create index if not exists dm_queue_sent_at_idx on public.dm_queue(sent_at);
create index if not exists dm_logs_created_at_idx on public.dm_logs(created_at);
create index if not exists kw_flows_active_keyword_idx on public.kw_flows(active, keyword);
