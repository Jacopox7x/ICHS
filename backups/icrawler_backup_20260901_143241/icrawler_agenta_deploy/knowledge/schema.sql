PRAGMA foreign_keys = ON;

CREATE TABLE kb_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

CREATE TABLE rule_priority (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    priority INTEGER NOT NULL UNIQUE,
    level TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE style_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    platform TEXT,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER,
    FOREIGN KEY (kb_version_id) REFERENCES kb_version(id)
);

CREATE TABLE platform_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    objective TEXT,
    structure TEXT,
    tone TEXT,
    hashtag_count INTEGER,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER,
    FOREIGN KEY (kb_version_id) REFERENCES kb_version(id)
);

CREATE TABLE content_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE hashtag_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE visual_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE cta_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE anti_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    severity TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE validation_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER NOT NULL,
    kb_version_id INTEGER
);

CREATE TABLE brief_constraints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field TEXT NOT NULL,
    rule TEXT NOT NULL,
    priority INTEGER DEFAULT 8
);

CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    kb_version_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    brief TEXT NOT NULL,
    expected_behavior TEXT NOT NULL,
    category TEXT,
    priority INTEGER DEFAULT 5,
    active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kb_version_id) REFERENCES kb_version(id)
);

CREATE TABLE lessons_learned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson TEXT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved INTEGER DEFAULT 0
);

CREATE TABLE rule_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_table TEXT NOT NULL,
    rule_id INTEGER NOT NULL,
    kb_version_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (kb_version_id) REFERENCES kb_version(id)
);

CREATE INDEX idx_style_priority ON style_rules(priority);
CREATE INDEX idx_platform_platform ON platform_rules(platform);
CREATE INDEX idx_content_priority ON content_rules(priority);
CREATE INDEX idx_hashtag_priority ON hashtag_rules(priority);
CREATE INDEX idx_visual_priority ON visual_rules(priority);
CREATE INDEX idx_cta_priority ON cta_rules(priority);
CREATE INDEX idx_anti_priority ON anti_patterns(priority);
CREATE INDEX idx_validation_priority ON validation_rules(priority);
CREATE INDEX idx_brief_field ON brief_constraints(field);
CREATE INDEX idx_test_case ON test_cases(case_id);
CREATE INDEX idx_rule_tags_tag ON rule_tags(tag);
CREATE INDEX idx_rule_tags_rule ON rule_tags(rule_table,rule_id);
