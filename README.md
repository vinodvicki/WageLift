# 🚀 WageLift - Quantify Your Purchasing Power Loss

[![CI/CD Pipeline](https://github.com/vinodvicki/WageLift/actions/workflows/ci.yml/badge.svg)](https://github.com/vinodvicki/WageLift/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/vinodvicki/WageLift/branch/main/graph/badge.svg)](https://codecov.io/gh/vinodvicki/WageLift)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/vinodvicki/WageLift)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**WageLift** is an AI-powered web/mobile platform that helps US employees quantify the **purchasing-power loss** of their salary due to inflation and craft **evidence-based raise requests**.

## 🎯 Problem & Solution

**Problem:** Real wages are not keeping up with CPI, yet most workers lack the data or confidence to negotiate effectively.

**Solution:** WageLift turns vague cost-of-living frustration into hard numbers and a polished negotiation brief—boosting employee earnings and aiding HR retention.

## ✨ Key Features

### 🧮 Inflation Gap Calculator
- Computes % and $ salary erosion since last raise
- Uses real CPI data from Bureau of Labor Statistics API
- Quantifies hidden pay cuts with precision

### 📊 Market Pay Benchmark
- Shows user's salary vs. local percentiles
- Integrates CareerOneStop / Payscale API data
- Provides external proof for salary negotiations

### 🤖 AI-Powered Raise Request Generator
- Drafts professional, data-cited emails/PDFs
- Uses GPT-4 Turbo for compelling arguments
- Removes writing friction with standardized tone

### 📈 Dashboard & History
- Visualizes CPI gap and market benchmarks
- Tracks negotiation progress over time
- Drives user re-engagement with insights

## 🏗️ Architecture

### Frontend
- **Next.js 14** with App Router
- **TypeScript** (strict mode)
- **Tailwind CSS** for styling
- **React Hook Form** + **Zod** validation
- **Recharts** for data visualization

### Backend
- **FastAPI (Python)** REST API
- **JWT Authentication** via Auth0
- **PostgreSQL** database on Supabase
- **Docker** containerization

### External Integrations
- **BLS CPI API** for inflation data
- **CareerOneStop/Payscale** for wage benchmarks
- **OpenAI GPT-4 Turbo** for content generation
- **Optional: Gusto/ADP** payroll sync

### Infrastructure
- **Vercel** (frontend hosting)
- **Railway** (backend hosting)
- **GitHub Actions** CI/CD
- **Cloudflare** proxy

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/wagelift/wagelift.git
   cd wagelift
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install
   
   # Install frontend dependencies
   cd frontend && npm install
   
   # Install backend dependencies
   cd ../backend && pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Frontend
   cp frontend/.env.example frontend/.env.local
   
   # Backend
   cp backend/.env.example backend/.env
   
   # Configure your API keys and database URLs
   ```

4. **Start development servers**
   ```bash
   # Start both frontend and backend
   npm run dev
   
   # Or start individually
   npm run dev:frontend  # http://localhost:3000
   npm run dev:backend   # http://localhost:8000
   ```

5. **Using Docker (Alternative)**
   ```bash
   # Development environment
   npm run docker:dev
   
   # Production environment
   npm run docker:prod
   ```

## 📁 Project Structure

```
wagelift/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── components/      # Reusable components
│   │   │   ├── lib/            # Utility functions
│   │   │   ├── hooks/          # Custom React hooks
│   │   │   └── types/          # TypeScript definitions
│   │   └── public/             # Static assets
 