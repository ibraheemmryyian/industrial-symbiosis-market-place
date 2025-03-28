BEGIN;

-- First ensure we have a UUID column in wastes table
ALTER TABLE wastes 
ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid();

-- Update all existing rows with new UUIDs
UPDATE wastes SET uuid_id = gen_random_uuid();

-- Make the new column NOT NULL
ALTER TABLE wastes
ALTER COLUMN uuid_id SET NOT NULL;

-- Add the new column to waste_matches
ALTER TABLE waste_matches
ADD COLUMN waste_uuid UUID;

-- Update matches with correct UUID references
UPDATE waste_matches m
SET waste_uuid = w.uuid_id
FROM wastes w
WHERE m.waste_id = w.id;

-- Make the new column NOT NULL
ALTER TABLE waste_matches
ALTER COLUMN waste_uuid SET NOT NULL;

-- Drop old foreign key constraint
ALTER TABLE waste_matches
DROP CONSTRAINT waste_matches_waste_id_fkey;

-- Add new foreign key constraint
ALTER TABLE waste_matches
ADD CONSTRAINT waste_matches_waste_uuid_fkey 
FOREIGN KEY (waste_uuid) REFERENCES wastes(uuid_id);

-- Update RLS policies to use new column
CREATE OR REPLACE POLICY "Match participants access" ON waste_matches
FOR ALL USING (
  consumer_id = auth.uid()
  OR EXISTS (
    SELECT 1 FROM wastes 
    WHERE uuid_id = waste_uuid AND producer_id = auth.uid()
  )
);

COMMIT;
