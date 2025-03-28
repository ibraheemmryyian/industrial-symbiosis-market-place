BEGIN;

-- Add foreign key to materials table
ALTER TABLE materials 
ADD CONSTRAINT materials_company_id_fkey 
FOREIGN KEY (company_id) 
REFERENCES companies(id) 
ON DELETE CASCADE;

-- Create proper matches-waste relationship
CREATE TABLE waste_matches (
    waste_id UUID REFERENCES waste(id) ON DELETE CASCADE,
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    PRIMARY KEY (waste_id, match_id)
);

COMMIT;
