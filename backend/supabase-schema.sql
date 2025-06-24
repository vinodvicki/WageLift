-- WageLift Supabase Database Schema
-- Designed for Auth0 JWT integration with Row-Level Security
-- Generated on: 2025-06-21

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row Level Security by default
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Payment frequency options
CREATE TYPE payment_frequency AS ENUM (
    'hourly',
    'weekly',
    'biweekly',
    'monthly',
    'annually'
);

-- Raise request status options
CREATE TYPE raise_request_status AS ENUM (
    'draft',
    'submitted',
    'approved',
    'rejected',
    'withdrawn'
);

-- Education level options
CREATE TYPE education_level AS ENUM (
    'high_school',
    'associates',
    'bachelors',
    'masters',
    'phd',
    'other'
);

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users table (main Auth0 integration point)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth0_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE CHECK (email ~* '^.+@.+\..+$'),
    full_name TEXT,
    profile_picture_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Create indexes for performance
CREATE INDEX idx_users_auth0_id ON public.users(auth0_id);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_created_at ON public.users(created_at);

-- User profiles (extended user information)
CREATE TABLE public.user_profiles (
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    job_title TEXT,
    industry TEXT,
    years_experience INTEGER CHECK (years_experience >= 0 AND years_experience <= 70),
    education_level education_level,
    location_postal_code TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id)
);

-- Salary entries (user salary history)
CREATE TABLE public.salary_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    base_salary NUMERIC(12, 2) NOT NULL CHECK (base_salary >= 0),
    bonus_amount NUMERIC(12, 2) DEFAULT 0 CHECK (bonus_amount >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    effective_date DATE NOT NULL,
    payment_frequency payment_frequency NOT NULL,
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for salary entries
CREATE INDEX idx_salary_entries_user_id ON public.salary_entries(user_id);
CREATE INDEX idx_salary_entries_current ON public.salary_entries(user_id) WHERE is_current = true;
CREATE INDEX idx_salary_entries_date ON public.salary_entries(effective_date DESC);

-- Benchmarks (public salary benchmark data)
CREATE TABLE public.benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_title TEXT NOT NULL,
    industry TEXT NOT NULL,
    location TEXT NOT NULL,
    min_salary NUMERIC(12, 2) NOT NULL CHECK (min_salary >= 0),
    max_salary NUMERIC(12, 2) NOT NULL CHECK (max_salary >= min_salary),
    median_salary NUMERIC(12, 2) NOT NULL CHECK (median_salary >= min_salary AND median_salary <= max_salary),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    data_source TEXT NOT NULL,
    sample_size INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for benchmarks
CREATE INDEX idx_benchmarks_job_title ON public.benchmarks(job_title);
CREATE INDEX idx_benchmarks_industry ON public.benchmarks(industry);
CREATE INDEX idx_benchmarks_location ON public.benchmarks(location);
CREATE INDEX idx_benchmarks_search ON public.benchmarks(job_title, industry, location);

-- Raise requests (user-generated raise requests)
CREATE TABLE public.raise_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    current_salary NUMERIC(12, 2) NOT NULL CHECK (current_salary >= 0),
    requested_salary NUMERIC(12, 2) NOT NULL CHECK (requested_salary >= 0),
    justification TEXT NOT NULL,
    status raise_request_status DEFAULT 'draft',
    benchmark_data JSONB,
    inflation_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for raise requests
CREATE INDEX idx_raise_requests_user_id ON public.raise_requests(user_id);
CREATE INDEX idx_raise_requests_status ON public.raise_requests(status);
CREATE INDEX idx_raise_requests_created_at ON public.raise_requests(created_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.salary_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.benchmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.raise_requests ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own profile" ON public.users
    FOR SELECT USING (auth0_id = auth.jwt() ->> 'sub');

CREATE POLICY "Users can update their own profile" ON public.users
    FOR UPDATE USING (auth0_id = auth.jwt() ->> 'sub');

-- User profiles policies
CREATE POLICY "Users can view their own user profile" ON public.user_profiles
    FOR SELECT USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Users can view public profiles" ON public.user_profiles
    FOR SELECT USING (is_public = true);

CREATE POLICY "Users can manage their own profile" ON public.user_profiles
    FOR ALL USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

-- Salary entries policies
CREATE POLICY "Users can view their own salary entries" ON public.salary_entries
    FOR SELECT USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Users can manage their own salary entries" ON public.salary_entries
    FOR ALL USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

-- Benchmarks policies (public read access)
CREATE POLICY "Anyone can view benchmarks" ON public.benchmarks
    FOR SELECT USING (true);

CREATE POLICY "Only service role can manage benchmarks" ON public.benchmarks
    FOR ALL USING (auth.role() = 'service_role');

-- Raise requests policies
CREATE POLICY "Users can view their own raise requests" ON public.raise_requests
    FOR SELECT USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

CREATE POLICY "Users can manage their own raise requests" ON public.raise_requests
    FOR ALL USING (
        user_id IN (
            SELECT id FROM public.users WHERE auth0_id = auth.jwt() ->> 'sub'
        )
    );

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON public.user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_salary_entries_updated_at 
    BEFORE UPDATE ON public.salary_entries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_benchmarks_updated_at 
    BEFORE UPDATE ON public.benchmarks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_raise_requests_updated_at 
    BEFORE UPDATE ON public.raise_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to ensure only one current salary entry per user
CREATE OR REPLACE FUNCTION ensure_single_current_salary()
RETURNS TRIGGER AS $$
BEGIN
    -- If setting is_current to true, set all other entries for this user to false
    IF NEW.is_current = true THEN
        UPDATE public.salary_entries 
        SET is_current = false 
        WHERE user_id = NEW.user_id AND id != NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER ensure_single_current_salary_trigger
    BEFORE INSERT OR UPDATE ON public.salary_entries
    FOR EACH ROW EXECUTE FUNCTION ensure_single_current_salary();

-- ============================================================================
-- REALTIME SUBSCRIPTIONS
-- ============================================================================

-- Enable realtime for user-specific data
ALTER PUBLICATION supabase_realtime ADD TABLE public.users;
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE public.salary_entries;
ALTER PUBLICATION supabase_realtime ADD TABLE public.raise_requests;

-- ============================================================================
-- SAMPLE DATA (Optional - for development)
-- ============================================================================

-- Insert sample benchmark data
INSERT INTO public.benchmarks (job_title, industry, location, min_salary, max_salary, median_salary, data_source, sample_size) VALUES
('Software Engineer', 'Technology', 'San Francisco, CA', 120000, 200000, 160000, 'Market Research 2024', 1500),
('Data Scientist', 'Technology', 'New York, NY', 110000, 180000, 145000, 'Salary Survey 2024', 800),
('Product Manager', 'Technology', 'Seattle, WA', 130000, 220000, 175000, 'Industry Report 2024', 600),
('Marketing Manager', 'Marketing', 'Los Angeles, CA', 80000, 140000, 110000, 'Market Analysis 2024', 900),
('Financial Analyst', 'Finance', 'Chicago, IL', 70000, 120000, 95000, 'Financial Survey 2024', 700);

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- Grant permissions on tables
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.salary_entries TO authenticated;
GRANT SELECT ON public.benchmarks TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.raise_requests TO authenticated;

-- Grant sequence permissions
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Comments for documentation
COMMENT ON TABLE public.users IS 'Main user table with Auth0 integration';
COMMENT ON TABLE public.user_profiles IS 'Extended user profile information';
COMMENT ON TABLE public.salary_entries IS 'User salary history and current compensation';
COMMENT ON TABLE public.benchmarks IS 'Public salary benchmark data for comparison';
COMMENT ON TABLE public.raise_requests IS 'User-generated raise requests with justification';

COMMENT ON COLUMN public.users.auth0_id IS 'Auth0 user identifier (sub claim from JWT)';
COMMENT ON COLUMN public.salary_entries.is_current IS 'Only one salary entry per user should have this as true';
COMMENT ON COLUMN public.benchmarks.sample_size IS 'Number of data points used for this benchmark';
COMMENT ON COLUMN public.raise_requests.benchmark_data IS 'JSON data containing relevant salary benchmarks';
COMMENT ON COLUMN public.raise_requests.inflation_data IS 'JSON data containing inflation calculations'; 