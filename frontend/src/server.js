
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');

const app = express();
const PORT = 5000;

app.use(bodyParser.json());

app.post('/scrape', async (req, res) => {
  const { url, options } = req.body;
  try {
    const response = await axios.post('http://localhost:5001/scrape', { url, options });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error scraping the website' });
  }
});

app.post('/ai-model', async (req, res) => {
  const { data } = req.body;
  try {
    const response = await axios.post('http://localhost:5002/ai-model', { data });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Error processing data with AI model' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});