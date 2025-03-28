/*
  # Create waste and match tables

  1. New Tables:
    - `wastes` - Stores waste materials available for matching
    - `waste_matches` - Stores matches between wastes and consumers
*/

-- Create enums first
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

-- Companies table with RLS
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their companies" ON companies
  FOR ALL USING (
    id IN (SELECT company_id FROM company_profiles WHERE user_id = auth.uid())
  );

-- Materials table with proper company relationship
CREATE TABLE materials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  quantity NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  description TEXT,
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wastes table with geospatial data
CREATE TABLE wastes (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  waste_type waste_type NOT NULL,
  waste_form waste_form NOT NULL,
  quantity FLOAT NOT NULL,
  unit TEXT NOT NULL,
  location TEXT NOT NULL,
  latitude FLOAT,
  longitude FLOAT,
  producer_id UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Matches table with explicit relationships
CREATE TABLE waste_matches (
  id SERIAL PRIMARY KEY,
  waste_id INTEGER NOT NULL REFERENCES wastes(id),
  consumer_id UUID NOT NULL REFERENCES auth.users(id),
  status match_status DEFAULT 'pending' NOT NULL,
  match_score FLOAT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS and create policies
ALTER TABLE wastes ENABLE ROW LEVEL SECURITY;
ALTER TABLE waste_matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Waste owners full access" ON wastes
  FOR ALL USING (producer_id = auth.uid());

CREATE POLICY "Public available wastes" ON wastes
  FOR SELECT USING (true);

CREATE POLICY "Match participants access" ON waste_matches
  FOR ALL USING (
    consumer_id = auth.uid()
    OR EXISTS (SELECT 1 FROM wastes WHERE id = waste_id AND producer_id = auth.uid())
  );
