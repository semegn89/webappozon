import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

// Простые стили
const styles = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    line-height: 1.6;
    color: #1f2937;
  }
  
  a {
    color: inherit;
    text-decoration: none;
  }
  
  button {
    cursor: pointer;
    font-family: inherit;
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  input, textarea {
    font-family: inherit;
    outline: none;
  }
  
  input:focus, textarea:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`

// Добавляем стили
const styleSheet = document.createElement('style')
styleSheet.textContent = styles
document.head.appendChild(styleSheet)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
