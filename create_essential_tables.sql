-- Essential WageLift Tables for Supabase
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (main Auth0 integration point)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth0_id TEXT UNIQUE,
    email TEXT UNIQUE,
    full_name TEXT,
    profile_picture_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Salary entries table
CREATE TABLE IF NOT EXISTS public.salary_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    current_salary NUMERIC(12, 2),
    last_raise_date DATE,
    job_title TEXT,
    location TEXT,
    experience_level TEXT,
    company_size TEXT,
    bonus_amount NUMERIC(12, 2),
    benefits TEXT[],
    equity_details TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Raise requests table
CREATE TABLE IF NOT EXISTS public.raise_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    current_salary NUMERIC(12, 2),
    requested_salary NUMERIC(12, 2),
    justification TEXT,
    status TEXT DEFAULT 'pending',
    letter_content TEXT,
    cpi_data JSONB,
    benchmark_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CPI data table
CREATE TABLE IF NOT EXISTS public.cpi_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    year INTEGER,
    period TEXT,
    value NUMERIC(10, 3),
    series_id TEXT,
    area TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Benchmarks table
CREATE TABLE IF NOT EXISTS public.benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_title TEXT,
    location TEXT,
    percentile_10 NUMERIC(12, 2),
    percentile_25 NUMERIC(12, 2),
    percentile_50 NUMERIC(12, 2),
    percentile_75 NUMERIC(12, 2),
    percentile_90 NUMERIC(12, 2),
    source TEXT,
    data_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_auth0_id ON public.users(auth0_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_salary_entries_user_id ON public.salary_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_raise_requests_user_id ON public.raise_requests(user_id);

-- Enable Row Level Security (optional - can be configured later)
-- ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.salary_entries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.raise_requests ENABLE ROW LEVEL SECURITY; 