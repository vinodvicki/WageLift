import { useState, useEffect } from 'react';

export default function TestPage() {
  const [backendStatus, setBackendStatus] = useState('checking...');
  const [frontendStatus] = useState('working');

  useEffect(() => {
    // Test backend connectivity
    fetch('http://localhost:8000/health')
      .then(response => response.json())
      .then(data => {
        setBackendStatus(`✅ Backend healthy: ${data.service} v${data.version}`);
      })
      .catch(error => {
        setBackendStatus(`❌ Backend error: ${error.message}`);
      });
  }, []);

  return (
    <div style={{ 
      padding: '40px', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      lineHeight: '1.6'
    }}>
      <h1 style={{ color: '#333', borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>
        🚀 WageLift System Status Test
      </h1>
      
      <div style={{ 
        background: '#f8f9fa', 
        padding: '20px', 
        borderRadius: '8px', 
        margin: '20px 0' 
      }}>
        <h2 style={{ color: '#495057', marginTop: '0' }}>Component Status</h2>
        <p><strong>Frontend:</strong> <span style={{ color: 'green' }}>✅ {frontendStatus}</span></p>
        <p><strong>Backend:</strong> <span>{backendStatus}</span></p>
      </div>

      <div style={{ 
        background: '#e7f3ff', 
        padding: '20px', 
        borderRadius: '8px', 
        margin: '20px 0' 
      }}>
        <h2 style={{ color: '#0066cc', marginTop: '0' }}>🎯 WageLift Features</h2>
        <ul style={{ paddingLeft: '20px' }}>
          <li>✅ Backend API Server (FastAPI)</li>
          <li>✅ Database Connection (SQLite)</li>
          <li>✅ Health Monitoring</li>
          <li>✅ API Documentation (/docs)</li>
          <li>⚠️  Frontend React/Next.js (has styling issues)</li>
          <li>🔧 Auth0 Integration (configured but optional)</li>
          <li>🔧 External APIs (BLS, CareerOneStop, OpenAI)</li>
        </ul>
      </div>

      <div style={{ 
        background: '#fff3cd', 
        padding: '20px', 
        borderRadius: '8px', 
        margin: '20px 0' 
      }}>
        <h2 style={{ color: '#856404', marginTop: '0' }}>🔗 Quick Links</h2>
        <ul style={{ listStyle: 'none', paddingLeft: '0' }}>
          <li style={{ margin: '10px 0' }}>
            <a href="http://localhost:8000/" style={{ color: '#007bff' }}>
              Backend API Root
            </a>
          </li>
          <li style={{ margin: '10px 0' }}>
            <a href="http://localhost:8000/docs" style={{ color: '#007bff' }}>
              API Documentation (Swagger)
            </a>
          </li>
          <li style={{ margin: '10px 0' }}>
            <a href="http://localhost:8000/health" style={{ color: '#007bff' }}>
              Health Check Endpoint
            </a>
          </li>
        </ul>
      </div>

      <div style={{ 
        background: '#d1ecf1', 
        padding: '20px', 
        borderRadius: '8px', 
        margin: '20px 0' 
      }}>
        <h2 style={{ color: '#0c5460', marginTop: '0' }}>📋 System Summary</h2>
        <p>
          <strong>WageLift</strong> is an AI-powered platform that helps US employees 
          quantify purchasing-power loss due to inflation and craft evidence-based raise requests.
        </p>
        <p>
          The backend is fully operational with enterprise-level features including 
          structured logging, monitoring, security middleware, and comprehensive API endpoints.
        </p>
      </div>

      <footer style={{ 
        textAlign: 'center', 
        marginTop: '40px', 
        color: '#6c757d',
        fontSize: '14px'
      }}>
        WageLift System Test Page | {new Date().toLocaleString()}
      </footer>
    </div>
  );
}