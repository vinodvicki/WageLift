-- Migration: 003_create_editor_tables.sql
-- Description: Create tables for the editor functionality (raise letters, versions, templates, sharing)
-- Date: 2024-01-15

-- Create raise_letters table
CREATE TABLE IF NOT EXISTS raise_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    document_metadata JSONB NOT NULL DEFAULT '{}',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes for raise_letters
CREATE INDEX IF NOT EXISTS idx_raise_letters_user_id ON raise_letters(user_id);
CREATE INDEX IF NOT EXISTS idx_raise_letters_user_active ON raise_letters(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_raise_letters_last_modified ON raise_letters(last_modified DESC);
CREATE INDEX IF NOT EXISTS idx_raise_letters_title ON raise_letters(title);

-- Create raise_letter_versions table
CREATE TABLE IF NOT EXISTS raise_letter_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES raise_letters(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    document_metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    change_summary TEXT
);

-- Create indexes for raise_letter_versions
CREATE INDEX IF NOT EXISTS idx_versions_document_id ON raise_letter_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_versions_document_version ON raise_letter_versions(document_id, version_number DESC);
CREATE INDEX IF NOT EXISTS idx_versions_created_at ON raise_letter_versions(created_at DESC);

-- Create raise_letter_templates table
CREATE TABLE IF NOT EXISTS raise_letter_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    category VARCHAR(100),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_by VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_modified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0
);

-- Create indexes for raise_letter_templates
CREATE INDEX IF NOT EXISTS idx_templates_category ON raise_letter_templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_public ON raise_letter_templates(is_public, is_active);
CREATE INDEX IF NOT EXISTS idx_templates_created_by ON raise_letter_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_templates_usage ON raise_letter_templates(usage_count DESC);

-- Create raise_letter_shares table
CREATE TABLE IF NOT EXISTS raise_letter_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES raise_letters(id) ON DELETE CASCADE,
    share_token VARCHAR(255) UNIQUE NOT NULL,
    shared_by VARCHAR(255) NOT NULL,
    shared_with VARCHAR(255),
    permissions VARCHAR(50) NOT NULL DEFAULT 'read',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    access_count INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create indexes for raise_letter_shares
CREATE INDEX IF NOT EXISTS idx_shares_document_id ON raise_letter_shares(document_id);
CREATE INDEX IF NOT EXISTS idx_shares_token ON raise_letter_shares(share_token);
CREATE INDEX IF NOT EXISTS idx_shares_shared_by ON raise_letter_shares(shared_by);
CREATE INDEX IF NOT EXISTS idx_shares_shared_with ON raise_letter_shares(shared_with);
CREATE INDEX IF NOT EXISTS idx_shares_expires ON raise_letter_shares(expires_at);

-- Create trigger for updating last_modified timestamp
CREATE OR REPLACE FUNCTION update_last_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to raise_letters table
DROP TRIGGER IF EXISTS update_raise_letters_last_modified ON raise_letters;
CREATE TRIGGER update_raise_letters_last_modified
    BEFORE UPDATE ON raise_letters
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified_column();

-- Apply trigger to raise_letter_templates table
DROP TRIGGER IF EXISTS update_templates_last_modified ON raise_letter_templates;
CREATE TRIGGER update_templates_last_modified
    BEFORE UPDATE ON raise_letter_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_last_modified_column();

-- Add some default templates
INSERT INTO raise_letter_templates (name, description, content, category, is_public, created_by) VALUES
(
    'Professional Standard',
    'A professional, formal template for salary adjustment requests',
    '<p>Dear [Manager Name],</p>
    <p>I am writing to request a review of my current compensation package. Based on my contributions to [Company Name] and current market conditions, I believe an adjustment to my salary is warranted.</p>
    <p><strong>Key Accomplishments:</strong></p>
    <ul>
        <li>[Achievement 1]</li>
        <li>[Achievement 2]</li>
        <li>[Achievement 3]</li>
    </ul>
    <p><strong>Market Analysis:</strong></p>
    <p>[Include market data and salary benchmarks]</p>
    <p>I would appreciate the opportunity to discuss this matter with you in person. Thank you for your time and consideration.</p>
    <p>Sincerely,<br>[Your Name]</p>',
    'professional',
    TRUE,
    'system'
),
(
    'Confident Approach',
    'A confident, assertive template emphasizing achievements',
    '<p>Dear [Manager Name],</p>
    <p>I am confident that my performance and contributions over the past [time period] have demonstrated significant value to [Company Name]. I am requesting a salary adjustment that reflects this value.</p>
    <p><strong>Quantifiable Impact:</strong></p>
    <ul>
        <li>[Specific metric or achievement]</li>
        <li>[Revenue impact or cost savings]</li>
        <li>[Process improvements]</li>
    </ul>
    <p>Based on current market data, professionals in my role with similar experience earn between [salary range]. My requested adjustment to [target salary] aligns with these market standards.</p>
    <p>I look forward to discussing how we can formalize this adjustment.</p>
    <p>Best regards,<br>[Your Name]</p>',
    'confident',
    TRUE,
    'system'
),
(
    'Collaborative Tone',
    'A collaborative, team-focused template',
    '<p>Dear [Manager Name],</p>
    <p>I hope this message finds you well. I wanted to schedule time to discuss my career development and compensation, as I believe this is an important conversation for both my growth and our team''s success.</p>
    <p><strong>Recent Contributions:</strong></p>
    <ul>
        <li>[Team collaboration example]</li>
        <li>[Mentoring or leadership role]</li>
        <li>[Cross-functional project success]</li>
    </ul>
    <p>I''ve researched current market conditions and believe there''s an opportunity to align my compensation more closely with industry standards while continuing to deliver exceptional results for our team.</p>
    <p>I''d love to discuss this further and explore how we can structure this in a way that works for everyone.</p>
    <p>Thank you for your continued support.</p>
    <p>Warm regards,<br>[Your Name]</p>',
    'collaborative',
    TRUE,
    'system'
);

-- Add comments to tables
COMMENT ON TABLE raise_letters IS 'Main table for storing user raise letter documents';
COMMENT ON TABLE raise_letter_versions IS 'Version history for raise letter documents';
COMMENT ON TABLE raise_letter_templates IS 'Reusable templates for raise letters';
COMMENT ON TABLE raise_letter_shares IS 'Sharing functionality for raise letters';

-- Add column comments
COMMENT ON COLUMN raise_letters.document_metadata IS 'JSON metadata including employee info, company details, etc.';
COMMENT ON COLUMN raise_letter_versions.change_summary IS 'Optional summary of what changed in this version';
COMMENT ON COLUMN raise_letter_shares.share_token IS 'Unique token for sharing documents';
COMMENT ON COLUMN raise_letter_shares.permissions IS 'Access level: read, comment, edit';

-- Migration completed successfully
SELECT 'Editor tables created successfully' AS status; 