-- EchoNet database schema. Run once in the Supabase SQL editor (or psql) before activating the workflow.

-- 1. Scan log (FR-11): one row per completed scan, written by "Log Scan for Audit & Retraining".
CREATE TABLE IF NOT EXISTS url_scans (
  id               bigserial PRIMARY KEY,
  scanned_at       timestamptz NOT NULL DEFAULT now(),
  url_hash         char(32)    NOT NULL,             -- MD5 of the normalised URL, same key as the Redis cache
  url              text        NOT NULL,             -- normalised URL, query secrets already removed
  wa_phone         char(64),                         -- salted SHA-256 of the sender's number (POPIA), never the number
  ml_prediction    text,                             -- 'phishing' | 'legitimate' from the Random Forest
  ml_probability   numeric(5,4),
  model_name       text,
  model_version    text,
  features         jsonb,                            -- the 23 features sent to /predict
  rag_threat_score numeric(5,4),
  rag_confidence   numeric(5,4),
  rag_assessment   jsonb,                            -- agent output incl. indicators and cited chunks
  final_verdict    text        NOT NULL CHECK (final_verdict IN ('PHISHING', 'LEGITIMATE')),
  risk_score       smallint    NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
  risk_category    text        NOT NULL CHECK (risk_category IN ('Low', 'Moderate', 'High')),
  scraped_ok       boolean     NOT NULL DEFAULT false,
  fired_rules      jsonb
);

CREATE INDEX IF NOT EXISTS url_scans_url_hash_idx   ON url_scans (url_hash);
CREATE INDEX IF NOT EXISTS url_scans_scanned_at_idx ON url_scans (scanned_at DESC);

-- 2. Threat knowledge base for the RAG agent (n8n Supabase Vector Store, OpenAI 1536-dim embeddings).
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id        bigserial PRIMARY KEY,
  content   text,
  metadata  jsonb,
  embedding vector(1536)
);

CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(1536),
  match_count int DEFAULT NULL,
  filter jsonb DEFAULT '{}'
) RETURNS TABLE (id bigint, content text, metadata jsonb, similarity float)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT d.id, d.content, d.metadata, 1 - (d.embedding <=> query_embedding) AS similarity
  FROM documents d
  WHERE d.metadata @> filter
  ORDER BY d.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
