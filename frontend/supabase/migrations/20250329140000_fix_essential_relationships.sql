BEGIN;

-- Fix materials foreign key constraint
ALTER TABLE materials 
ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE;

-- Fix matches relationship
ALTER TABLE waste_matches
ALTER COLUMN waste_id TYPE INTEGER,
ADD CONSTRAINT waste_matches_waste_id_fkey FOREIGN KEY (waste_id) REFERENCES wastes(id);

-- Update RLS policies if needed
CREATE OR REPLACE POLICY "Users can manage their materials" 
ON materials
FOR ALL
TO authenticated
USING (company_id IN (
  SELECT id FROM companies 
  WHERE id IN (
    SELECT company_id FROM company_profiles 
    WHERE company_profiles.company_id = auth.uid()
  )
));

COMMIT;
