const express = require('express');
const fs = require('fs');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors());

// Define paths based on your specific D: drive structure
const LEDGER_PATH = path.join(__dirname, 'ledger', 'forensic_audit_ledger.jsonl');
const REPORT_PATH = path.join(__dirname, 'reports', 'forensic_audit.json');

app.get('/api/live-logs', (req, res) => {
  try {
    if (!fs.existsSync(LEDGER_PATH)) return res.json([]);
    
    const data = fs.readFileSync(LEDGER_PATH, 'utf8');
    // Converts .jsonl lines into a clean JSON array for your React Dashboard
    const logs = data.trim().split('\n')
      .filter(line => line.trim() !== "")
      .map(line => JSON.parse(line));
      
    res.json(logs);
  } catch (err) {
    console.error("Error reading ledger:", err);
    res.status(500).json({ error: "Could not read ledger file" });
  }
});

app.listen(3001, () => {
  console.log('--------------------------------------');
  console.log('HawkGrid Log Bridge is now LIVE');
  console.log('Listening for Kali/Curl logs on port 3001');
  console.log('--------------------------------------');
});