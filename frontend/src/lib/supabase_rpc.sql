-- SQL to create the stored procedure in Supabase
create or replace function public.create_company_and_profile(
  user_id uuid,
  profile_data jsonb,
  company_data jsonb default '{}'::jsonb
) returns uuid
language plpgsql
security definer
as $$
declare
  company_id uuid;
  user_email text;
begin
  -- Get user email (use provided email from company_data if available)
  select coalesce(company_data->>'email', email) into user_email 
  from auth.users 
  where id = user_id;

  -- Get existing company if user already has one
  select company_id into company_id 
  from company_profiles 
  where user_id = create_company_and_profile.user_id
  limit 1;

  -- Create new company if none exists
  if company_id is null then
    company_id := gen_random_uuid();
    insert into public.companies (
      id, 
      name, 
      email,
      created_at
    )
    values (
      company_id, 
      profile_data->>'organization_name',
      user_email,
      now()
    );
  end if;

  -- Link user to company
  insert into public.company_profiles (
    company_id,
    user_id,
    role,
    location,
    interests,
    organization_type,
    materials_of_interest,
    sustainability_goals
  ) values (
    company_id,
    user_id,
    profile_data->>'role',
    profile_data->>'location',
    profile_data->>'interests',
    profile_data->>'organization_type',
    profile_data->>'materials_of_interest',
    profile_data->>'sustainability_goals'
  );

  return company_id;
end;
$$;
