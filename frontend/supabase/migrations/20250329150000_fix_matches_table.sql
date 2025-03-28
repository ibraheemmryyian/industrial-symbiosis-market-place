BEGIN;

-- Rename waste_matches to matches if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'waste_matches') THEN
        ALTER TABLE waste_matches RENAME TO matches;
    END IF;
END $$;

-- Ensure proper foreign key relationships
ALTER TABLE matches
ALTER COLUMN waste_id TYPE UUID USING waste_id::TEXT::UUID,
ALTER COLUMN consumer_id TYPE UUID USING consumer_id::TEXT::UUID,
ADD CONSTRAINT matches_waste_id_fkey FOREIGN KEY (waste_id) REFERENCES wastes(id),
ADD CONSTRAINT matches_consumer_id_fkey FOREIGN KEY (consumer_id) REFERENCES companies(id);

-- Update RLS policies
CREATE OR REPLACE POLICY "Users can view their matches" 
ON matches
FOR SELECT
TO authenticated
USING (
    waste_id IN (SELECT id FROM wastes WHERE company_id IN (
        SELECT company_id FROM company_profiles WHERE user_id = auth.uid()
    ))
    OR
    consumer_id IN (SELECT id FROM companies WHERE id IN (
        SELECT company_id FROM company_profiles WHERE user_id = auth.uid()
    ))
);

CREATE OR REPLACE POLICY "Users can update their matches" 
ON matches
FOR UPDATE
TO authenticated
USING (
    consumer_id IN (SELECT id FROM companies WHERE id IN (
        SELECT company_id FROM company_profiles WHERE user_id = auth.uid()
    ))
)
WITH CHECK (
    consumer_id IN (SELECT id FROM companies WHERE id IN (
        SELECT company_id FROM company_profiles WHERE user_id = auth.uid()
    ))
);

COMMIT;
