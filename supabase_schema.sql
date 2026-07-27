-- Run this once in your Supabase project's SQL Editor (Project → SQL Editor → New query).

create table if not exists waitlist_signups (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name text not null,
  email text not null unique,
  age_group text not null,
  role text not null,
  message text
);

-- Row Level Security stays off for this table, which is fine here: the app
-- only ever talks to Supabase using the secret service_role key from the
-- server side (Render/Vercel), which always bypasses RLS anyway. Just make
-- sure SUPABASE_SERVICE_KEY is never sent to the browser or committed to git.
