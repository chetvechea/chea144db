-- Run once in the Supabase SQL editor as project administrator.
create extension if not exists pgcrypto with schema extensions;

create table public.app_licenses (
  id uuid primary key default gen_random_uuid(),
  key_hash text unique not null,
  expires_at timestamptz not null,
  revoked boolean not null default false,
  created_at timestamptz not null default now()
);
create table public.app_release (
  id integer primary key check (id = 1),
  latest_version text not null,
  minimum_version text not null
);
insert into public.app_release values (1, '1.0.0', '1.0.0');
alter table public.app_licenses enable row level security;
alter table public.app_release enable row level security;
revoke all on public.app_licenses, public.app_release from anon, authenticated;

-- The client can verify a high-entropy bearer key, but cannot list or edit rows.
create function public.check_license(submitted_key text) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  lic public.app_licenses%rowtype;
  rel public.app_release%rowtype;
  reason text;
begin
  if length(submitted_key) not between 20 and 200 then
    raise exception 'Invalid key length';
  end if;
  select * into lic from public.app_licenses
    where key_hash = encode(extensions.digest(submitted_key, 'sha256'), 'hex');
  reason := case when lic.id is null then 'invalid'
    when lic.revoked then 'revoked'
    when lic.expires_at <= now() then 'expired' else 'active' end;
  select * into strict rel from public.app_release where id = 1;
  return jsonb_build_object('valid', reason = 'active', 'reason', reason,
    'expires_at', lic.expires_at, 'latest_version', rel.latest_version,
    'minimum_version', rel.minimum_version);
end;
$$;
revoke all on function public.check_license(text) from public;
grant execute on function public.check_license(text) to anon, authenticated;

-- Admin only: select * from public.issue_license(1); or issue_license(12).
-- Copy the returned key immediately. Only its SHA-256 hash is stored.
create function public.issue_license(months integer)
returns table (license_id uuid, license_key text, expires_at timestamptz)
language plpgsql security definer set search_path = '' as $$
declare
  new_key text := 'SP-' || encode(extensions.gen_random_bytes(32), 'hex');
begin
  if months not in (1, 12) or months is null then
    raise exception 'Choose 1 or 12 months';
  end if;
  return query insert into public.app_licenses as l (key_hash, expires_at)
    values (encode(extensions.digest(new_key, 'sha256'), 'hex'), now() + make_interval(months => months))
    returning l.id, new_key, l.expires_at;
end;
$$;
revoke all on function public.issue_license(integer) from public, anon, authenticated;
