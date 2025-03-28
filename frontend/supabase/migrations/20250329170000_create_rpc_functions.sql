BEGIN;

CREATE OR REPLACE FUNCTION public.create_company_and_profile(
  company_data JSONB,
  profile_data JSONB,
  user_id UUID
) 
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  company_id UUID;
BEGIN
  -- Insert company
  INSERT INTO companies (name)
  VALUES (company_data->>'name')
  RETURNING id INTO company_id;

  -- Insert company profile
  INSERT INTO company_profiles (
    company_id,
    user_id,
    industry,
    location,
    description
  ) VALUES (
    company_id,
    user_id,
    profile_data->>'industry',
    profile_data->>'location',
    profile_data->>'description'
  );

  RETURN company_id;
END;
$$;

COMMIT;
