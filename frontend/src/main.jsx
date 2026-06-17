import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { initPushNotifications } from './services/pushNotifications'
import './index.css'

initPushNotifications().catch(() => {})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
