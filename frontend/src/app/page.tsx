export default function HomePage() {
  return (
    <div>
      {/* Navigation */}
      <nav className="navbar">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <a href="/" className="logo">
            <div className="logo-icon">W</div>
            WageLift
          </a>
          <div className="nav-links hidden md:flex space-x-8">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#demo">Demo</a>
            <a href="/dashboard/salary" className="btn btn-primary">Get Started</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-gradient py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-4xl mx-auto animate-fade-in">
            <h1 className="heading-xl">
              Stop Being <span className="gradient-text">Underpaid</span>
              <br />Start Getting What You're Worth
            </h1>
            <p className="text-lead text-gray-200 max-w-3xl mx-auto">
              WageLift uses AI and real market data to calculate your exact raise amount, then generates a professional letter that gets results. Join thousands who've increased their salary.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <a href="/dashboard/salary" className="btn btn-accent btn-large">
                Calculate My Raise
              </a>
              <a href="#demo" className="btn btn-secondary btn-large">
                Watch Demo
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="heading-lg">Why WageLift Works</h2>
            <p className="text-lead max-w-3xl mx-auto">
              Our AI-powered platform combines market data, inflation calculations, and proven negotiation strategies to maximize your earning potential.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card card-elevated text-center p-8 animate-slide-up">
              <div className="feature-icon">📊</div>
              <h3 className="heading-sm">Real Market Data</h3>
              <p className="text-body">
                Access live salary data from thousands of companies and positions to know exactly what you should be earning.
              </p>
            </div>
            
            <div className="card card-elevated text-center p-8 animate-slide-up">
              <div className="feature-icon">🤖</div>
              <h3 className="heading-sm">AI-Powered Analysis</h3>
              <p className="text-body">
                Our advanced AI analyzes your role, experience, and market conditions to calculate your precise raise amount.
              </p>
            </div>
            
            <div className="card card-elevated text-center p-8 animate-slide-up">
              <div className="feature-icon">📝</div>
              <h3 className="heading-sm">Professional Letters</h3>
              <p className="text-body">
                Get a customized, professional raise request letter that presents your case with data-backed confidence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="heading-lg">How It Works</h2>
            <p className="text-lead max-w-3xl mx-auto">
              Get your raise in three simple steps. Our proven process has helped thousands of professionals increase their salary.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center animate-scale">
              <div className="step-number">1</div>
              <h3 className="heading-sm">Enter Your Details</h3>
              <p className="text-body">
                Tell us about your current role, salary, location, and experience level.
              </p>
            </div>
            
            <div className="text-center animate-scale">
              <div className="step-number">2</div>
              <h3 className="heading-sm">Get Your Analysis</h3>
              <p className="text-body">
                Our AI analyzes market data and calculates your exact raise amount with supporting evidence.
              </p>
            </div>
            
            <div className="text-center animate-scale">
              <div className="step-number">3</div>
              <h3 className="heading-sm">Present Your Case</h3>
              <p className="text-body">
                Use our professional letter template to confidently request your well-deserved raise.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="heading-lg">See WageLift in Action</h2>
            <p className="text-lead max-w-3xl mx-auto">
              Watch how Sarah, a software engineer, used WageLift to secure a $15,000 raise in just two weeks.
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <div className="card card-elevated overflow-hidden">
              <div className="aspect-video bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <div className="w-0 h-0 border-l-[12px] border-l-white border-y-[8px] border-y-transparent ml-1"></div>
                  </div>
                  <p className="text-lg font-semibold">Demo Video Coming Soon</p>
                  <p className="text-gray-200">See real results from real users</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="heading-lg mb-4">Ready to Get the Raise You Deserve?</h2>
          <p className="text-lead text-gray-200 max-w-2xl mx-auto mb-8">
            Join thousands of professionals who have successfully increased their salary using WageLift's data-driven approach.
          </p>
          <a href="/dashboard/salary" className="btn btn-accent btn-large">
            Start Your Raise Calculator
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="logo mb-4">
                <div className="logo-icon">W</div>
                WageLift
              </div>
              <p className="text-gray-400">
                Empowering professionals to earn what they're worth through data-driven salary negotiations.
              </p>
            </div>
            
            <div>
              <h4>Product</h4>
              <a href="#features" className="footer-links">Features</a>
              <a href="#how-it-works" className="footer-links">How It Works</a>
              <a href="#demo" className="footer-links">Demo</a>
              <a href="/dashboard/salary" className="footer-links">Get Started</a>
            </div>
            
            <div>
              <h4>Resources</h4>
              <a href="#" className="footer-links">Salary Guide</a>
              <a href="#" className="footer-links">Negotiation Tips</a>
              <a href="#" className="footer-links">Success Stories</a>
              <a href="#" className="footer-links">Blog</a>
            </div>
            
            <div>
              <h4>Company</h4>
              <a href="#" className="footer-links">About</a>
              <a href="#" className="footer-links">Privacy</a>
              <a href="#" className="footer-links">Terms</a>
              <a href="#" className="footer-links">Contact</a>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2024 WageLift. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
} 