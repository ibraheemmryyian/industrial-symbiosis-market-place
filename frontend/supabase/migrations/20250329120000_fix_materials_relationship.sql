BEGIN;

-- Create companies table with proper security
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their companies" 
ON companies
FOR ALL
TO authenticated
USING (id IN (
  SELECT company_id FROM company_profiles 
  WHERE company_profiles.user_id = auth.uid()
));

-- Create materials table with proper foreign key
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  quantity NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  description TEXT,
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE materials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their materials" 
ON materials
FOR ALL
TO authenticated
USING (company_id IN (
  SELECT company_id FROM company_profiles 
  WHERE company_profiles.user_id = auth.uid()
));

COMMIT;
