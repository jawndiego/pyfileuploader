// pages/new-page.tsx
import { useState } from 'react';

function chatBot() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    console.log('Submitting query:', query);  // <-- Add this line
    // Send a request to your server with the query
    const response = await fetch('get-info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (response.ok) {
      const data = await response.json();
      setResult(data);  // Set the result state with the response data
    } else {
      console.error('Request failed');
    }
  };

  return (
    <div>
      <h1>ask away m8</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Enter your query"
        />
        <button type="submit">Submit</button>
      </form>

      {result && (
        <div>
          <h2>Result:</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default chatBot;
