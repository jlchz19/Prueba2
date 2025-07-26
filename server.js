const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, 'dist/temp-frontend/browser')));

// Send all requests to index.html
app.get('/*', function(req, res) {
  res.sendFile(path.join(__dirname, 'dist/temp-frontend/browser/index.html'));
});

// Start the app by listening on the default port
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 