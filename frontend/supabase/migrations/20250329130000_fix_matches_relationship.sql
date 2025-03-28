BEGIN;

-- Drop the incorrect join table if it exists
DROP TABLE IF EXISTS waste_matches;

-- Recreate the proper matches table from initial migration
CREATE TABLE waste_matches (
  id SERIAL PRIMARY KEY,
  waste_id INTEGER NOT NULL REFERENCES wastes(id),
  consumer_id UUID NOT NULL REFERENCES auth.users(id),
  status match_status DEFAULT 'pending' NOT NULL,
  match_score FLOAT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Re-enable RLS and policies
ALTER TABLE waste_matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Match participants access" ON waste_matches
  FOR ALL USING (
    consumer_id = auth.uid()
    OR EXISTS (SELECT 1 FROM wastes WHERE id = waste_id AND producer_id = auth.uid())
  );

COMMIT;
