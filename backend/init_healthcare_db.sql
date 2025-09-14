CREATE TABLE IF NOT EXISTS healthcare_user (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS healthcare_feedback (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title BYTEA,
    title_nonce BYTEA,
    body BYTEA,
    body_nonce BYTEA,
    created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES healthcare_user(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS healthcare_insight (
    feedback_id VARCHAR(36) PRIMARY KEY,
    sentiment VARCHAR(8) NOT NULL,
    key_topics TEXT[],
    action_required BOOLEAN,
    summary TEXT,
    tokens INT,
    latency DOUBLE PRECISION,
    CONSTRAINT fk_feedback
        FOREIGN KEY (feedback_id)
        REFERENCES healthcare_feedback(id)
        ON DELETE CASCADE
);