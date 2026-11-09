-- Fencing token prevents stale workers from finalising a reclaimed job.
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS claim_token UUID;
