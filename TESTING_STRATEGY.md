# WageLift Comprehensive Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for WageLift's authentication system and overall application architecture. Following 2025 enterprise testing patterns, our strategy ensures robust, secure, and performant authentication flows across the entire stack.

## Testing Architecture

### 🎯 **Testing Pyramid**

```
    /\
   /E2E\     ← End-to-End Tests (Browser automation)
  /______\
 /        \
/Integration\ ← Integration Tests (API + Auth flows)
\____________/
/            \
/   Unit Tests  \ ← Component & Function Tests
\______________/
```

### 🔧 **Technology Stack**

**Frontend Testing:**
- **Jest** - Test runner and assertion library
- **React Testing Library** - Component testing utilities
- **Playwright** - End-to-end browser testing
- **MSW (Mock Service Worker)** - API mocking

**Backend Testing:**
- **pytest** - Python test framework
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client testing
- **pytest-benchmark** - Performance benchmarking
- **Locust** - Load testing

**Auth & Security Testing:**
- **Auth0 Mock Server** - JWT validation testing
- **Supabase Test Client** - Database operation testing
- **OWASP ZAP** - Security vulnerability scanning

## 🧪 Phase 1: Core Testing Foundation

### Backend Testing Setup

#### pytest Configuration (`backend/pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --asyncio-mode=auto
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --benchmark-only
    --benchmark-sort=mean
markers =
    unit: Unit tests
    integration: Integration tests
    auth: Authentication tests
    performance: Performance tests
    security: Security tests
```

#### Core Test Fixtures (`backend/tests/conftest.py`)
```python
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def auth0_mock():
    """Mock Auth0 JWKS and validation."""
    with patch("app.core.auth.get_jwks_keys") as mock_jwks, \
         patch("app.core.auth.validate_token") as mock_validate:
        
        mock_jwks.return_value = [{"kid": "test", "kty": "RSA"}]
        mock_validate.return_value = {
            "sub": "auth0|test123",
            "email": "test@wagelift.com"
        }
        yield {"jwks": mock_jwks, "validate": mock_validate}

@pytest.fixture
async def supabase_mock():
    """Mock Supabase operations."""
    with patch("app.services.supabase_service.SupabaseService") as mock_service:
        instance = mock_service.return_value
        instance.get_user_by_auth0_id = AsyncMock(return_value={
            "id": "test-user-id",
            "auth0_id": "auth0|test123",
            "email": "test@wagelift.com"
        })
        yield instance
```

### Frontend Testing Setup

#### Jest Configuration (`frontend/jest.config.js`)
```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/app/layout.tsx',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

#### Test Utilities (`frontend/src/__tests__/utils/test-utils.tsx`)
```typescript
import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { UserProvider } from '@auth0/nextjs-auth0/client'

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <UserProvider>
      {children}
    </UserProvider>
  )
}

const customRender = (ui: React.ReactElement, options?: RenderOptions) =>
  render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Mock factories
export const createMockUser = (overrides = {}) => ({
  sub: 'auth0|test123456789',
  email: 'test@wagelift.com',
  name: 'Test User',
  ...overrides,
})

export const createMockAuth0Context = (overrides = {}) => ({
  user: createMockUser(),
  isLoading: false,
  error: undefined,
  ...overrides,
})
```

## 🔐 Authentication Testing Scenarios

### Auth0 Integration Tests

#### JWT Validation Testing
```python
# backend/tests/test_auth0_integration.py

@pytest.mark.auth
class TestAuth0Integration:
    
    @pytest.mark.asyncio
    async def test_jwks_key_fetching_success(self, auth0_mock):
        """Test successful JWKS key retrieval."""
        keys = await get_jwks_keys()
        assert len(keys) == 1
        assert keys[0]["kid"] == "test"
    
    @pytest.mark.asyncio
    async def test_jwt_validation_expired_token(self):
        """Test expired token handling."""
        with patch("app.core.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Token expired")
            
            with pytest.raises(HTTPException) as exc:
                await validate_token("expired.token")
            assert exc.value.status_code == 401
    
    @pytest.mark.asyncio
    async def test_redis_cache_performance(self, benchmark):
        """Benchmark Redis cache operations."""
        async def cache_operation():
            return await get_jwks_keys()
        
        result = await benchmark(cache_operation)
        assert result is not None
```

#### Frontend Auth Component Testing
```typescript
// frontend/src/__tests__/auth/auth-provider.test.tsx

describe('AuthProvider', () => {
  it('should create Supabase user on first Auth0 login', async () => {
    const mockUser = createMockUser()
    const mockAuth0Context = createMockAuth0Context({ user: mockUser })
    
    jest.mocked(useUser).mockReturnValue(mockAuth0Context)
    
    render(<AuthProvider><div>Test</div></AuthProvider>)
    
    await waitFor(() => {
      expect(mockSupabaseClient.from).toHaveBeenCalledWith('users')
    })
  })
  
  it('should handle authentication errors gracefully', () => {
    const errorContext = createMockAuth0Context({
      user: undefined,
      error: new Error('Auth failed'),
    })
    
    jest.mocked(useUser).mockReturnValue(errorContext)
    
    render(<AuthProvider><div>Test</div></AuthProvider>)
    
    expect(screen.queryByText('Test')).not.toBeInTheDocument()
  })
})
```

### Supabase Integration Tests

#### Database Operations Testing
```python
# backend/tests/test_supabase_integration.py

@pytest.mark.integration
class TestSupabaseIntegration:
    
    @pytest.mark.asyncio
    async def test_user_creation_success(self, supabase_mock):
        """Test successful user creation."""
        user_data = {
            "auth0_id": "auth0|test123",
            "email": "test@wagelift.com",
            "name": "Test User"
        }
        
        result = await supabase_mock.create_user(user_data)
        
        assert result["id"] == "test-user-id"
        assert result["email"] == "test@wagelift.com"
    
    @pytest.mark.asyncio
    async def test_duplicate_email_handling(self, supabase_mock):
        """Test duplicate email constraint."""
        supabase_mock.create_user.side_effect = IntegrityError(
            "duplicate key", None, None
        )
        
        with pytest.raises(ValueError) as exc:
            await supabase_mock.create_user({"email": "existing@test.com"})
        assert "duplicate" in str(exc.value).lower()
```

#### Row-Level Security Testing
```sql
-- backend/tests/sql/test_rls_policies.sql

-- Test user can only access their own data
SELECT plan(3);

-- Setup test data
INSERT INTO auth.users (id, email) VALUES ('test-user-1', 'user1@test.com');
INSERT INTO auth.users (id, email) VALUES ('test-user-2', 'user2@test.com');

-- Test RLS enforcement
SELECT ok(
    (SELECT count(*) FROM users WHERE auth.uid() = 'test-user-1') = 1,
    'User can access their own record'
);

SELECT ok(
    (SELECT count(*) FROM users WHERE auth.uid() = 'test-user-2') = 0,
    'User cannot access other user records'
);

SELECT finish();
```

## 🚀 Phase 2: Integration & Performance Testing

### End-to-End Testing with Playwright

#### E2E Test Configuration (`frontend/playwright.config.ts`)
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './src/__tests__/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
})
```

#### Auth Flow E2E Tests
```typescript
// frontend/src/__tests__/e2e/auth-flow.spec.ts

test.describe('Authentication Flow', () => {
  test('complete login flow', async ({ page }) => {
    await page.goto('/login')
    
    // Click login button
    await page.click('button:has-text("Login with Auth0")')
    
    // Mock Auth0 redirect
    await page.route('**/auth0.com/**', (route) => {
      route.fulfill({
        status: 302,
        headers: {
          location: '/api/auth/callback?code=test-auth-code',
        },
      })
    })
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard')
    
    // Verify user menu
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })
  
  test('protected route access without auth', async ({ page }) => {
    await page.goto('/dashboard')
    
    // Should redirect to login
    await expect(page).toHaveURL('/login')
  })
})
```

### Performance Testing

#### Backend Performance Benchmarks
```python
# backend/tests/test_performance.py

@pytest.mark.performance
class TestAuthPerformance:
    
    @pytest.mark.benchmark(group="auth")
    def test_jwt_validation_performance(self, benchmark, auth0_mock):
        """Benchmark JWT validation speed."""
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.test.signature"
        
        result = benchmark(validate_token, token)
        assert result is not None
    
    @pytest.mark.benchmark(group="database")
    def test_user_lookup_performance(self, benchmark, supabase_mock):
        """Benchmark user lookup speed."""
        result = benchmark(
            supabase_mock.get_user_by_auth0_id, 
            "auth0|test123"
        )
        assert result is not None
```

#### Load Testing with Locust
```python
# backend/tests/load/locustfile.py

from locust import HttpUser, task, between

class AuthLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for load test."""
        self.headers = {
            "Authorization": "Bearer test-token",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def protected_endpoint(self):
        """Test protected endpoint under load."""
        self.client.get("/api/protected", headers=self.headers)
    
    @task(1)
    def user_profile(self):
        """Test user profile endpoint."""
        self.client.get("/api/user/profile", headers=self.headers)
```

### Frontend Performance Testing
```typescript
// frontend/src/__tests__/performance/auth-performance.test.tsx

describe('Auth Component Performance', () => {
  it('should render AuthProvider within performance budget', async () => {
    const startTime = performance.now()
    
    render(<AuthProvider><div>Test</div></AuthProvider>)
    
    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument()
    })
    
    const endTime = performance.now()
    const renderTime = endTime - startTime
    
    // Should render within 50ms
    expect(renderTime).toBeLessThan(50)
  })
  
  it('should handle rapid auth state changes', async () => {
    const component = render(<AuthProvider><div>Test</div></AuthProvider>)
    
    // Simulate 10 rapid state changes
    for (let i = 0; i < 10; i++) {
      const mockContext = createMockAuth0Context({
        isLoading: i % 2 === 0
      })
      jest.mocked(useUser).mockReturnValue(mockContext)
      component.rerender(<AuthProvider><div>Test {i}</div></AuthProvider>)
    }
    
    // Should handle without performance degradation
    expect(screen.getByText(/Test/)).toBeInTheDocument()
  })
})
```

## 🔒 Phase 3: Security & Monitoring Testing

### Security Testing

#### OWASP Top 10 Coverage
```python
# backend/tests/test_security.py

@pytest.mark.security
class TestSecurityVulnerabilities:
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection."""
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.get(f"/api/user?id={malicious_input}")
        
        # Should not execute malicious SQL
        assert response.status_code in [400, 401, 404]
    
    def test_xss_protection(self, client):
        """Test XSS protection."""
        xss_payload = "<script>alert('xss')</script>"
        
        response = client.post("/api/user/profile", json={
            "name": xss_payload
        })
        
        # Should sanitize input
        assert "<script>" not in response.text
    
    def test_csrf_protection(self, client):
        """Test CSRF protection."""
        response = client.post("/api/user/update", json={
            "name": "Updated Name"
        })
        
        # Should require CSRF token or proper auth
        assert response.status_code in [401, 403]
```

#### Auth-Specific Security Tests
```python
@pytest.mark.security
class TestAuthSecurity:
    
    def test_token_leakage_prevention(self, client):
        """Test token is not exposed in logs."""
        with patch("app.core.logging.logger") as mock_logger:
            client.get("/api/protected", headers={
                "Authorization": "Bearer secret-token"
            })
            
            # Verify token not in logs
            logged_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            assert not any("secret-token" in call for call in logged_calls)
    
    def test_session_fixation_protection(self, client):
        """Test session fixation protection."""
        # Attempt session fixation attack
        response = client.get("/api/auth/callback", cookies={
            "sessionid": "attacker-controlled-session"
        })
        
        # Should generate new session
        assert "Set-Cookie" in response.headers
```

### Monitoring Integration Tests
```python
# backend/tests/test_metrics_integration.py

@pytest.mark.integration
class TestMetricsIntegration:
    
    def test_auth_metrics_collection(self, client, metrics_registry):
        """Test authentication metrics are collected."""
        # Perform authenticated request
        client.get("/api/protected", headers={
            "Authorization": "Bearer valid-token"
        })
        
        # Verify metrics were recorded
        auth_counter = metrics_registry.get_sample_value(
            "auth_requests_total", {"status": "success"}
        )
        assert auth_counter > 0
    
    def test_performance_metrics_tracking(self, client, metrics_registry):
        """Test performance metrics tracking."""
        client.get("/api/user/profile")
        
        # Verify response time was recorded
        histogram = metrics_registry.get_sample_value(
            "http_request_duration_seconds_count"
        )
        assert histogram > 0
```

## 📊 Test Coverage & Reporting

### Coverage Requirements
- **Unit Tests**: 90% line coverage minimum
- **Integration Tests**: 80% critical path coverage
- **E2E Tests**: 100% user journey coverage
- **Security Tests**: 100% OWASP Top 10 coverage

### Automated Testing Pipeline
```yaml
# .github/workflows/test.yml
name: Comprehensive Testing

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest-cov pytest-benchmark
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/unit/ --cov=app --cov-report=xml
      
      - name: Run integration tests
        run: |
          cd backend
          pytest tests/integration/ --cov=app --cov-append
      
      - name: Run security tests
        run: |
          cd backend
          pytest tests/security/ -m security
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run unit tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright install
          npm run test:e2e

  load-testing:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Run load tests
        run: |
          cd backend
          pip install locust
          locust -f tests/load/locustfile.py --headless -u 50 -r 5 -t 60s
```

## 🎯 Testing Best Practices

### Test Organization
- **Arrange-Act-Assert** pattern for all tests
- **Single responsibility** - one concept per test
- **Descriptive names** - what, when, expected outcome
- **Independent tests** - no test dependencies
- **Fast execution** - unit tests under 100ms

### Mock Strategy
- **Mock external dependencies** (Auth0, Supabase, Redis)
- **Use real objects for internal dependencies**
- **Mock time-sensitive operations**
- **Verify interactions when behavior matters**

### Data Management
- **Test data factories** for consistent test data
- **Database rollback** after each test
- **Isolated test environments**
- **Seed data for E2E tests**

### Performance Testing
- **Baseline measurements** for regression detection
- **Load testing in staging** environment
- **Memory leak detection** in long-running tests
- **Cache performance validation**

## 🚀 Implementation Roadmap

### Week 1: Foundation Setup
- [ ] Configure pytest with async support
- [ ] Set up Jest with React Testing Library
- [ ] Create core test fixtures and utilities
- [ ] Implement Auth0 and Supabase mocking

### Week 2: Core Test Coverage
- [ ] Unit tests for authentication functions
- [ ] Component tests for auth UI
- [ ] Integration tests for auth flows
- [ ] Database operation tests

### Week 3: Advanced Testing
- [ ] E2E tests with Playwright
- [ ] Performance benchmarks
- [ ] Security vulnerability tests
- [ ] Load testing setup

### Week 4: CI/CD Integration
- [ ] GitHub Actions workflow
- [ ] Coverage reporting
- [ ] Performance regression detection
- [ ] Security scanning automation

## 📈 Success Metrics

### Quality Metrics
- **Test Coverage**: >90% for critical paths
- **Test Speed**: Unit tests <100ms, Integration <5s
- **Flaky Test Rate**: <2% of test runs
- **Bug Escape Rate**: <1% to production

### Performance Metrics
- **Auth Response Time**: <200ms p95
- **Database Query Time**: <50ms p95
- **UI Render Time**: <100ms for auth components
- **Load Test Success**: 1000 concurrent users

### Security Metrics
- **Zero Critical Vulnerabilities**
- **OWASP Top 10 Coverage**: 100%
- **Auth Token Security**: No leakage in logs
- **Session Security**: Proper invalidation

## 📚 Additional Resources

### Documentation
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [pytest Documentation](https://docs.pytest.org/)
- [Auth0 Testing Guide](https://auth0.com/docs/libraries/auth0-react#testing)
- [Supabase Testing Guide](https://supabase.com/docs/guides/getting-started/tutorials/with-nextjs#testing)

### Tools & Libraries
- **Visual Regression**: Percy, Chromatic
- **API Testing**: Postman, Insomnia
- **Security Scanning**: Snyk, OWASP ZAP
- **Performance Monitoring**: Lighthouse CI, WebPageTest

---

This comprehensive testing strategy ensures WageLift's authentication system is robust, secure, and performant. The layered approach provides defense in depth from unit tests through production monitoring, maintaining our high standards for enterprise-grade software development. 