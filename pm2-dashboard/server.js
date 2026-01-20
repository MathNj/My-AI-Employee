const express = require('express');
const pm2 = require('pm2');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// PM2 API endpoint
app.get('/api/processes', (req, res) => {
  pm2.list((err, processes) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(processes);
  });
});

// PM2 logs endpoint
app.get('/api/logs', (req, res) => {
  const lines = parseInt(req.query.lines) || 100;
  pm2.retrieveLogs(lines, (err, logs) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(logs);
  });
});

// PM2 metadata endpoint
app.get('/api/metadata', (req, res) => {
  pm2.describe((err, metadata) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(metadata);
  });
});

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`PM2 Dashboard running on http://localhost:${PORT}`);
});

// Connect to PM2
pm2.connect((err) => {
  if (err) {
    console.error('Error connecting to PM2:', err);
    process.exit(1);
  }
  console.log('Connected to PM2 daemon');
});

// Cleanup on exit
process.on('SIGINT', () => {
  pm2.disconnect();
  process.exit(0);
});
