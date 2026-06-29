export default function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>AICC — AI Command Center</h1>
      <p>Locked In with Kareesa · Frontend is live.</p>
      <ul>
        <li><a href="http://localhost:8080/docs">API Docs (FastAPI)</a></li>
        <li><a href="http://localhost:8080/health">API Health</a></li>
        <li><a href="http://localhost:5678">n8n Workflows</a></li>
        <li><a href="http://localhost:3000">Supabase Studio</a></li>
      </ul>
    </div>
  )
}
