-- WageLift Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create all necessary tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS \
uuid-ossp\;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    auth0_id TEXT UNIQUE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Salary entries table
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
    employment_type TEXT DEFAULT 'full_time',
    benefits_value DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Raise requests table
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
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CPI data table
CREATE TABLE IF NOT EXISTS cpi_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    cpi_value DECIMAL(10,4) NOT NULL,
    category TEXT DEFAULT 'All Urban Consumers',
    region TEXT DEFAULT 'US',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(year, month, category, region)
);

-- Benchmarks table
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(job_title, location, source, data_date)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON users(auth0_id);
CREATE INDEX IF NOT EXISTS idx_salary_entries_user_id ON salary_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_raise_requests_user_id ON raise_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_cpi_data_year_month ON cpi_data(year, month);
CREATE INDEX IF NOT EXISTS idx_benchmarks_job_location ON benchmarks(job_title, location);

-- Insert sample data for testing
INSERT INTO cpi_data (year, month, cpi_value, category, region) VALUES
    (2024, 1, 310.326, 'All Urban Consumers', 'US'),
    (2024, 2, 310.326, 'All Urban Consumers', 'US'),
    (2024, 3, 312.230, 'All Urban Consumers', 'US')
ON CONFLICT (year, month, category, region) DO NOTHING;

-- Success message
SELECT 'WageLift database schema created successfully!' as message;
