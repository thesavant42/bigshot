-- PostgreSQL schema for bigshot reconnaissance application
-- Migrated from SQLite schema with PostgreSQL-specific optimizations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- URLs table for storing discovered URLs
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    domain TEXT,
    timestamp TEXT,
    status_code INTEGER,
    mime_type TEXT,
    tags TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table for background task management
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    type TEXT,
    domain TEXT,
    status TEXT,
    progress INTEGER,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Import status table for tracking import operations
CREATE TABLE IF NOT EXISTS import_status (
    id SERIAL PRIMARY KEY,
    status TEXT,
    detail TEXT,
    progress INTEGER,
    total INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table for URL-specific annotations
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    url_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(url_id) REFERENCES urls(id) ON DELETE CASCADE
);

-- Text notes table for general annotations
CREATE TABLE IF NOT EXISTS text_notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- JWT cookies table for authentication token storage
CREATE TABLE IF NOT EXISTS jwt_cookies (
    id SERIAL PRIMARY KEY,
    token TEXT,
    header TEXT,
    payload TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Screenshots table for storing screenshot information
CREATE TABLE IF NOT EXISTS screenshots (
    id SERIAL PRIMARY KEY,
    url TEXT,
    method TEXT,
    screenshot_path TEXT,
    thumbnail_path TEXT,
    status_code INTEGER DEFAULT 0,
    ip_addresses TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sitezips table for storing site archive information
CREATE TABLE IF NOT EXISTS sitezips (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    method TEXT DEFAULT 'GET',
    zip_path TEXT,
    screenshot_path TEXT,
    thumbnail_path TEXT,
    status_code INTEGER DEFAULT 0,
    ip_addresses TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assets table for storing asset information
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    path TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    content_type_affinity TEXT DEFAULT '',
    load_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Domains table for hierarchical subdomain storage
-- This table supports hierarchical/collapsible subdomain data
CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    root_domain TEXT NOT NULL,
    subdomain TEXT NOT NULL,
    source TEXT NOT NULL,
    tags TEXT DEFAULT '',
    cdx_indexed BOOLEAN DEFAULT FALSE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subdomain, source)
);

-- Performance indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain);
CREATE INDEX IF NOT EXISTS idx_urls_created_at ON urls(created_at);
CREATE INDEX IF NOT EXISTS idx_urls_domain_status ON urls(domain, status_code);

CREATE INDEX IF NOT EXISTS idx_domains_root ON domains(root_domain);
CREATE INDEX IF NOT EXISTS idx_domains_subdomain ON domains(subdomain);
CREATE INDEX IF NOT EXISTS idx_domains_source ON domains(source);
CREATE INDEX IF NOT EXISTS idx_domains_fetched_at ON domains(fetched_at);
CREATE INDEX IF NOT EXISTS idx_domains_root_created ON domains(root_domain, created_at);
CREATE INDEX IF NOT EXISTS idx_domains_hierarchical ON domains(root_domain, subdomain);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(type);
CREATE INDEX IF NOT EXISTS idx_jobs_domain ON jobs(domain);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_assets_path ON assets(path);

CREATE INDEX IF NOT EXISTS idx_notes_url_id ON notes(url_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);

-- Constraints for data integrity
ALTER TABLE domains ADD CONSTRAINT chk_domains_subdomain_not_empty CHECK (subdomain != '');
ALTER TABLE domains ADD CONSTRAINT chk_domains_root_domain_not_empty CHECK (root_domain != '');
ALTER TABLE domains ADD CONSTRAINT chk_domains_source_not_empty CHECK (source != '');

ALTER TABLE urls ADD CONSTRAINT chk_urls_url_not_empty CHECK (url != '');
ALTER TABLE jobs ADD CONSTRAINT chk_jobs_status_valid CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_urls_updated_at BEFORE UPDATE ON urls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_domains_updated_at BEFORE UPDATE ON domains
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_text_notes_updated_at BEFORE UPDATE ON text_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE domains IS 'Stores hierarchical subdomain information for reconnaissance targets';
COMMENT ON COLUMN domains.root_domain IS 'The root domain (e.g., example.com)';
COMMENT ON COLUMN domains.subdomain IS 'The full subdomain (e.g., www.example.com, stage.www.example.com)';
COMMENT ON COLUMN domains.source IS 'The source of discovery (e.g., crt.sh, virustotal, shodan)';
COMMENT ON COLUMN domains.tags IS 'User-defined tags for categorization';
COMMENT ON COLUMN domains.cdx_indexed IS 'Whether the domain has been indexed in CDX';

COMMENT ON TABLE urls IS 'Stores discovered URLs with metadata';
COMMENT ON TABLE jobs IS 'Manages background enumeration and processing jobs';
COMMENT ON TABLE notes IS 'User annotations for specific URLs';
COMMENT ON TABLE text_notes IS 'General user notes not tied to specific URLs';