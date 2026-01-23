-- RESET AND ALIGN SCHEMA
-- WARNING: This will drop the existing 'users' and 'analysis_history' tables to ensure schema compatibility.

DROP TABLE IF EXISTS public.analysis_history;
DROP TABLE IF EXISTS public.users;

-- 1. Create 'users' table (Synced from Clerk)
create table public.users (
  id text primary key, -- Stores Clerk User ID (e.g., user_2...)
  email text unique not null,
  name text,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Create 'analysis_history' table
create table public.analysis_history (
  id uuid default gen_random_uuid() primary key,
  clerk_user_id text references public.users(id), -- Link to users table
  user_email text,
  filename text not null,
  prediction text not null,
  confidence float not null,
  is_noisy boolean default false,
  tips text[],
  report_url text,
  image_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Indexes for performance
create index idx_analysis_user_id on public.analysis_history(clerk_user_id);

-- 4. Storage Buckets (Run this if you haven't created them in UI)
insert into storage.buckets (id, name, public) 
values ('uploads', 'uploads', true)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public) 
values ('reports', 'reports', true)
on conflict (id) do nothing;

-- 5. RLS Policies
alter table public.users enable row level security;
create policy "Public Access Users" on public.users for all using (true);

alter table public.analysis_history enable row level security;
create policy "Public Access History" on public.analysis_history for all using (true);
