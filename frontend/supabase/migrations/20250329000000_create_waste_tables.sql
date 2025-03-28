/*
  # Create waste and match tables

  1. New Tables:
    - `wastes` - Stores waste materials available for matching
    - `waste_matches` - Stores matches between wastes and consumers
*/

CREATE TYPE waste_type AS ENUM (
  'chemical',
  'metal',
  'plastic',
  'organic',
  'electronic',
  'other'
);

CREATE TYPE waste_form AS ENUM (
  'heat',
  'material'
);

CREATE TYPE match_status AS ENUM (
  'pending',
  'accepted',
  'rejected',
  'completed'
);

CREATE TABLE wastes (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  waste_type waste_type NOT NULL,
  waste_form waste_form NOT NULL,
  quantity FLOAT NOT NULL,
  unit TEXT NOT NULL,
  location TEXT NOT NULL,
  available_from TIMESTAMPTZ,
  available_to TIMESTAMPTZ,
  requires_special_handling BOOLEAN DEFAULT FALSE,
  special_handling_notes TEXT,
  is_available BOOLEAN DEFAULT TRUE,
  latitude FLOAT,
  longitude FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  producer_id UUID REFERENCES auth.users(id) NOT NULL,
  embedding TEXT,
  keywords TEXT,
  category TEXT
);

CREATE TABLE waste_matches (
  id SERIAL PRIMARY KEY,
  waste_id INTEGER REFERENCES wastes(id) NOT NULL,
  consumer_id UUID REFERENCES auth.users(id) NOT NULL,
  match_score FLOAT NOT NULL,
  status match_status DEFAULT 'pending' NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  matched_quantity FLOAT,
  matched_unit TEXT,
  notes TEXT,
  producer_notes TEXT,
  consumer_notes TEXT,
  producer_rating INTEGER,
  consumer_rating INTEGER,
  producer_feedback TEXT,
  consumer_feedback TEXT,
  match_reason TEXT,
  sustainability_score FLOAT
);

-- Enable RLS for both tables
ALTER TABLE wastes ENABLE ROW LEVEL SECURITY;
ALTER TABLE waste_matches ENABLE ROW LEVEL SECURITY;

-- Policies for wastes table
CREATE POLICY "Users can manage their own wastes"
  ON wastes
  FOR ALL
  TO authenticated
  USING (producer_id = auth.uid());

CREATE POLICY "Users can read available wastes"
  ON wastes
  FOR SELECT
  TO authenticated
  USING (is_available = TRUE);

-- Policies for waste_matches table
CREATE POLICY "Users can manage their own matches"
  ON waste_matches
  FOR ALL
  TO authenticated
  USING (consumer_id = auth.uid() OR EXISTS (
    SELECT 1 FROM wastes WHERE wastes.id = waste_matches.waste_id AND wastes.producer_id = auth.uid()
  ));

CREATE POLICY "Users can read their own matches"
  ON waste_matches
  FOR SELECT
  TO authenticated
  USING (consumer_id = auth.uid() OR EXISTS (
    SELECT 1 FROM wastes WHERE wastes.id = waste_matches.waste_id AND wastes.producer_id = auth.uid()
  ));
