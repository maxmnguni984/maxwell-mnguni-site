---
name: supabase
description: Add a Postgres backend, auth, storage, or realtime to an app with Supabase. Use when an app needs to save data, sign users in, upload files, or when writing schema, migrations, or row level security policies.
---

# Supabase

The default backend for apps that need to persist anything. Postgres with auth,
storage, and an auto-generated API on top, so there is no server to run.

## Getting the keys right

Two keys, and confusing them is a security incident:

- **Publishable / anon key** — safe in client code. It is public by design.
  Every request it makes is constrained by row level security.
- **Secret / service role key** — bypasses row level security entirely. It
  belongs only on a server or in an edge function. Never in client code, never
  in a `VITE_`-prefixed variable, never committed.

Anything prefixed `VITE_`, `NEXT_PUBLIC_`, or `PUBLIC_` is compiled into the
JavaScript bundle and readable by anyone. Only the publishable key goes there.

## Row level security is not optional

A new table is readable and writable by anyone holding the anon key until RLS
is enabled. Enabling RLS with no policies denies everything, which is the safe
default — then add policies deliberately.

```sql
alter table public.projects enable row level security;

create policy "owners read their own"
  on public.projects for select
  using (auth.uid() = user_id);

create policy "owners insert their own"
  on public.projects for insert
  with check (auth.uid() = user_id);
```

`using` filters the rows a statement can see; `with check` validates rows being
written. An insert policy needs `with check` — `using` alone will not stop a
user writing a row owned by someone else.

Write a policy per operation. A single `for all` policy is almost always too
broad.

**Verify policies by testing as a signed-in user, not with the service key.**
The service key passes every policy, so testing with it proves nothing.

For a public form that anyone may submit but nobody may read — a waitlist,
contact form, feedback — allow insert to `anon` and grant no select at all.

## Schema

- Let Postgres generate ids: `id uuid primary key default gen_random_uuid()`.
- `created_at timestamptz not null default now()`. Always `timestamptz`, never
  `timestamp` — the latter silently discards the offset.
- Foreign keys with a deliberate `on delete` behaviour. `cascade` when the
  child is meaningless without the parent, `restrict` when deletion should be
  refused.
- Index the columns you filter and join on. Postgres indexes the primary key,
  nothing else.
- `check` constraints for values with a fixed set. The database is the last
  place that can enforce it.

## Migrations

Every schema change is a migration file, committed. Never click a change into
the dashboard and forget it — the next environment will not have it and nobody
will know why.

Migrations run forward against real data. Adding a `not null` column to a table
with rows fails unless it has a default. Renaming a column breaks any client
still deploying the old bundle — add the new column, migrate the reads, then
drop the old one in a later release.

## Querying

The client returns `{ data, error }` and does **not** throw. An unchecked
`error` is the most common Supabase bug — the code carries on with `data` as
`null`.

```ts
const { data, error } = await supabase.from('projects').select('*')
if (error) { /* decide what the user sees */ }
```

Select the columns you need rather than `*`. Paginate with `.range()`; the API
caps rows returned and silently truncating a list looks like missing data.

## Auth

`getSession()` reads from local storage and is fast but spoofable client-side —
fine for deciding what UI to show, never for authorization. Authorization is
RLS's job, enforced in the database.

Handle the states explicitly: loading, signed out, signed in. Treating
"loading" as "signed out" produces a login-screen flash on every refresh.

Set the redirect URLs for every environment — local, preview, and production.
A missing redirect URL is the usual cause of a login that dead-ends.

## Practical notes

- Free-tier projects pause after inactivity and need restoring before they
  respond. A paused project looks exactly like a broken connection string.
- Pick a region near the users. Latency to the database is on every request,
  and data residency may not be optional.
- Generate TypeScript types from the schema and regenerate them after every
  migration. Stale types are worse than none.
