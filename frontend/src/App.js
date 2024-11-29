import React, { useState } from 'react';
import { FaSearch } from "react-icons/fa";
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [options, setOptions] = useState({
    title: false,
    images: false,
    links: false,
  });

  const handleChange = (e) => {
    const { name, checked } = e.target;
    setOptions({
      ...options,
      [name]: checked,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, options }),
      });
      const data = await response.json();
      console.log('Scraped Data:', data);
      // Send data to AI model server
      const aiResponse = await fetch('http://localhost:5000/ai-model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ data }),
      });
      const aiData = await aiResponse.json();
      console.log('AI Model Response:', aiData);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <form className='web-scraper' onSubmit={handleSubmit}>
          <div className="search-container">
            <input
              type="text"
              placeholder="Enter URL to scrape"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="search-bar"
            />
            <button type="submit" className="search-button">
              <FaSearch className='search-icon' />
            </button>
          </div>
          <div className="checkboxes">
            <label>
              <input
                type="checkbox"
                name="title"
                checked={options.title}
                onChange={handleChange}
              />
              Project Content
            </label>
            <label>
              <input
                type="checkbox"
                name="images"
                checked={options.images}
                onChange={handleChange}
              />
              Project Images
            </label>
            <label>
              <input
                type="checkbox"
                name="links"
                checked={options.links}
                onChange={handleChange}
              />
              Rewiews
            </label>
          </div>
        </form>
      </header>
    </div>
  );
}

export default App;
