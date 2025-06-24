# 🚀 WageLift Demo Setup Guide

## ✅ **Quick Start (Recommended)**

### **Option 1: One-Click Demo (Easiest)**
```bash
# From the WageLift root directory
start-demo.bat
```

This will:
- ✅ Start the backend server at http://localhost:8000
- ✅ Open the comprehensive demo in your browser
- ✅ Show live API integration status
- ✅ Display all features and functionality

### **Option 2: Manual Setup**

1. **Start Backend Server**
   ```bash
   cd backend
   python demo_app.py
   ```
   - Server will run at http://localhost:8000
   - Health check: http://localhost:8000/health

2. **Open Frontend Demo**
   ```bash
   cd frontend
   start working-demo.html
   ```

---

## 🎯 **What You'll See**

### **Live Demo Features**
- **🧮 Interactive CPI Calculator** - Calculate your purchasing power loss
- **📊 Real-time Market Analysis** - Compare your salary to market rates
- **🤖 AI Letter Preview** - See GPT-4 generated raise request letters
- **📈 Data Visualizations** - Charts and graphs of your analysis
- **🔗 API Integration Status** - Live backend connectivity testing
- **📱 Responsive Design** - Works on desktop, tablet, and mobile

### **Backend API Endpoints**
- `GET /health` - Server health check
- `GET /api/v1/demo/features` - Available features list
- `POST /api/v1/cpi/calculate` - CPI gap calculation
- `POST /api/v1/salary/benchmark` - Market benchmarking
- `POST /api/v1/raise-letter/generate` - AI letter generation

---

## 🔧 **Troubleshooting**

### **If Backend Won't Start**
```bash
# Check Python version (need 3.8+)
python --version

# Install dependencies
cd backend
pip install -r requirements-basic.txt

# Run demo server
python demo_app.py
```

### **If Frontend Won't Open**
- Double-click `frontend/working-demo.html` directly
- Or open in browser: `file:///path/to/frontend/working-demo.html`

### **If API Calls Fail**
- Ensure backend is running on http://localhost:8000
- Check Windows Firewall isn't blocking port 8000
- Try accessing http://localhost:8000/health directly

### **For Next.js Development (Advanced)**
```bash
cd frontend

# Clean install
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Or use simplified config
cp package-simple.json package.json
npm install

# Start development server
npm run dev
```

---

## 🎨 **Customization Options**

### **Visual Customization**
The demo uses Tailwind CSS classes. You can easily modify:

1. **Colors**: Change `indigo-600` to `blue-600`, `green-600`, etc.
2. **Gradients**: Modify gradient classes like `from-indigo-50 to-cyan-50`
3. **Fonts**: Update font classes like `font-bold`, `text-2xl`
4. **Spacing**: Adjust padding/margin with `p-8`, `m-4`, etc.
5. **Animations**: Modify hover effects and transitions

### **Content Customization**
- **Hero Section**: Update main headline and description
- **Feature Cards**: Modify the 3 main feature descriptions
- **Calculator**: Adjust default values and calculation logic
- **AI Letter**: Customize the sample letter template
- **Company Info**: Update branding and contact information

### **Functionality Customization**
- **Calculation Logic**: Modify inflation rates and formulas
- **API Endpoints**: Add new backend integrations
- **Charts**: Customize data visualization with Chart.js
- **Forms**: Add new input fields and validation
- **Export Features**: Enhance PDF/email functionality

---

## 📊 **Project Status**

### **Completed Features (93.33%)**
- ✅ **Task 1-13**: Core platform functionality
- ✅ **Task 15**: Gusto OAuth integration (just completed!)
- ✅ CPI gap calculation with BLS data
- ✅ Market benchmarking with CareerOneStop
- ✅ AI-powered raise letter generation
- ✅ Email and PDF export functionality
- ✅ Auth0 authentication system
- ✅ PostgreSQL database with Supabase
- ✅ Docker containerization
- ✅ Comprehensive testing suite

### **Remaining Work (6.67%)**
- ⏳ **Task 14**: React Native mobile dashboard (optional)

### **Technology Stack**
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11, PostgreSQL
- **Authentication**: Auth0 with JWT tokens
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4 Turbo
- **APIs**: BLS, CareerOneStop, Gusto OAuth
- **Deployment**: Docker, Vercel/Railway ready

---

## 🚀 **Next Steps**

1. **Run the demo** using `start-demo.bat`
2. **Explore all features** in the interactive demo
3. **Customize the design** to match your preferences
4. **Test API integrations** with the live backend
5. **Review the codebase** for production deployment
6. **Deploy to production** when ready

---

## 📞 **Support**

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Try the simplified setup options
4. Review the browser console for errors
5. Check backend logs for API issues

The demo is designed to work out-of-the-box with minimal setup required!

---

**Happy customizing! 🎉** 