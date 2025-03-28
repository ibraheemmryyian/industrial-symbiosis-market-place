-- SQL to create the stored procedure in Supabase
create or replace function public.create_company_and_profile(
  user_id uuid,
  profile_data jsonb
) returns void
language plpgsql
security definer
as $$
begin
  -- Insert company if not exists (bypasses RLS due to security definer)
  insert into public.companies (id, name)
  values (user_id, 'New Company')
  on conflict (id) do nothing;

  -- Insert profile
  insert into public.company_profiles (
    company_id,
    role,
    location,
    interests,
    organization_type,
    materials_of_interest,
    sustainability_goals
  ) values (
    user_id,
    profile_data->>'role',
    profile_data->>'location',
    profile_data->>'interests',
    profile_data->>'organization_type',
    profile_data->>'materials_of_interest',
    profile_data->>'sustainability_goals'
  );
end;
$$;
