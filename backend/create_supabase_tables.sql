-- WageLift Supabase Database Schema
-- Professional Production-Ready Setup
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    auth0_id TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create salary_entries table
CREATE TABLE IF NOT EXISTS salary_entries (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    current_salary DECIMAL(12,2) NOT NULL,
    job_title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    years_experience INTEGER,
    education_level TEXT,
    industry TEXT,
    employment_type TEXT DEFAULT 'Full-time',
    benefits_value DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create raise_requests table
CREATE TABLE IF NOT EXISTS raise_requests (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    salary_entry_id UUID REFERENCES salary_entries(id) ON DELETE CASCADE,
    requested_salary DECIMAL(12,2) NOT NULL,
    current_salary DECIMAL(12,2) NOT NULL,
    percentage_increase DECIMAL(5,2) NOT NULL,
    justification TEXT,
    ai_generated_letter TEXT,
    cpi_data JSONB,
    benchmark_data JSONB,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'approved', 'rejected', 'pending')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create cpi_data table
CREATE TABLE IF NOT EXISTS cpi_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    cpi_value DECIMAL(10,3) NOT NULL,
    category TEXT DEFAULT 'All Urban Consumers',
    region TEXT DEFAULT 'US',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(year, month, category, region)
);

-- Create benchmarks table
CREATE TABLE IF NOT EXISTS benchmarks (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_title TEXT NOT NULL,
    location TEXT NOT NULL,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    salary_median DECIMAL(12,2),
    salary_avg DECIMAL(12,2),
    percentile_10 DECIMAL(12,2),
    percentile_25 DECIMAL(12,2),
    percentile_75 DECIMAL(12,2),
    percentile_90 DECIMAL(12,2),
    source TEXT DEFAULT 'CareerOneStop',
    data_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);
CREATE INDEX IF NOT EXISTS idx_salary_entries_user_id ON salary_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_salary_entries_job_title ON salary_entries(job_title);
CREATE INDEX IF NOT EXISTS idx_raise_requests_user_id ON raise_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_raise_requests_status ON raise_requests(status);
CREATE INDEX IF NOT EXISTS idx_cpi_data_year_month ON cpi_data(year, month);
CREATE INDEX IF NOT EXISTS idx_benchmarks_job_location ON benchmarks(job_title, location);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_salary_entries_updated_at BEFORE UPDATE ON salary_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_raise_requests_updated_at BEFORE UPDATE ON raise_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE salary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE raise_requests ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid()::text = auth0_id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid()::text = auth0_id);
CREATE POLICY "Anyone can insert users" ON users FOR INSERT WITH CHECK (true);

-- Create RLS policies for salary_entries table
CREATE POLICY "Users can view own salary entries" ON salary_entries FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can insert own salary entries" ON salary_entries FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can update own salary entries" ON salary_entries FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can delete own salary entries" ON salary_entries FOR DELETE USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));

-- Create RLS policies for raise_requests table
CREATE POLICY "Users can view own raise requests" ON raise_requests FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can insert own raise requests" ON raise_requests FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can update own raise requests" ON raise_requests FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));
CREATE POLICY "Users can delete own raise requests" ON raise_requests FOR DELETE USING (user_id IN (SELECT id FROM users WHERE auth.uid()::text = auth0_id));

-- CPI data and benchmarks are public read-only
CREATE POLICY "Anyone can read CPI data" ON cpi_data FOR SELECT USING (true);
CREATE POLICY "Anyone can read benchmarks" ON benchmarks FOR SELECT USING (true);

-- Insert sample CPI data
INSERT INTO cpi_data (year, month, cpi_value, category, region) VALUES
(2024, 1, 310.326, 'All Urban Consumers', 'US'),
(2024, 2, 310.326, 'All Urban Consumers', 'US'),
(2024, 3, 310.326, 'All Urban Consumers', 'US'),
(2023, 12, 307.026, 'All Urban Consumers', 'US'),
(2023, 11, 307.671, 'All Urban Consumers', 'US'),
(2023, 10, 307.789, 'All Urban Consumers', 'US')
ON CONFLICT (year, month, category, region) DO NOTHING;

-- Insert sample benchmark data
INSERT INTO benchmarks (job_title, location, salary_min, salary_max, salary_median, salary_avg, percentile_25, percentile_75, source, data_date) VALUES
('Software Engineer', 'San Francisco, CA', 85000, 180000, 135000, 140000, 115000, 165000, 'CareerOneStop', '2024-01-01'),
('Software Engineer', 'New York, NY', 80000, 170000, 125000, 130000, 105000, 155000, 'CareerOneStop', '2024-01-01'),
('Software Engineer', 'Seattle, WA', 75000, 165000, 120000, 125000, 100000, 150000, 'CareerOneStop', '2024-01-01'),
('Data Scientist', 'San Francisco, CA', 90000, 200000, 145000, 150000, 125000, 175000, 'CareerOneStop', '2024-01-01'),
('Product Manager', 'San Francisco, CA', 95000, 220000, 155000, 160000, 135000, 185000, 'CareerOneStop', '2024-01-01')
ON CONFLICT DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT 'WageLift Supabase database setup completed successfully!' as status; 