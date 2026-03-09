import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// #region agent log
window.addEventListener('error', (e) => { fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'main.tsx:window.error',message:'uncaught error',data:{message:e.message,stack:e.error?.stack},hypothesisId:'H4',timestamp:Date.now()})}).catch(()=>{}); });
window.addEventListener('unhandledrejection', (e) => { fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'main.tsx:unhandledrejection',message:'unhandled rejection',data:{reason:String(e.reason)},hypothesisId:'H4',timestamp:Date.now()})}).catch(()=>{}); });
// #endregion

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
