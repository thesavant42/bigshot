CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL CHECK(url != ''),
    domain TEXT,
    timestamp TEXT,
    status_code INTEGER,
    mime_type TEXT,
    tags TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    domain TEXT,
    status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress INTEGER,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS import_status (
    id INTEGER PRIMARY KEY,
    status TEXT,
    detail TEXT,
    progress INTEGER,
    total INTEGER
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(url_id) REFERENCES urls(id)
);

CREATE TABLE IF NOT EXISTS text_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jwt_cookies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT,
    header TEXT,
    payload TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    method TEXT,
    screenshot_path TEXT,
    thumbnail_path TEXT,
    status_code INTEGER DEFAULT 0,
    ip_addresses TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sitezips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    method TEXT DEFAULT 'GET',
    zip_path TEXT,
    screenshot_path TEXT,
    thumbnail_path TEXT,
    status_code INTEGER DEFAULT 0,
    ip_addresses TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    content_type_affinity TEXT DEFAULT '',
    load_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_domain TEXT NOT NULL CHECK(root_domain != ''),
    subdomain TEXT NOT NULL CHECK(subdomain != ''),
    source TEXT NOT NULL CHECK(source != ''),
    tags TEXT DEFAULT '',
    cdx_indexed INTEGER DEFAULT 0,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subdomain, source)
);

CREATE INDEX IF NOT EXISTS idx_urls_domain ON urls(domain);
CREATE INDEX IF NOT EXISTS idx_domains_root ON domains(root_domain);
CREATE INDEX IF NOT EXISTS idx_domains_subdomain ON domains(subdomain);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);


