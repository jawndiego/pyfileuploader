import React, { useState, FormEvent, KeyboardEvent, useRef, useEffect } from 'react';

interface Message {
  query: string;
  answer: string;
}

function ChatBot() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<Message[]>([]);
  const [loadingIndex, setLoadingIndex] = useState<number | null>(null);
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return; // Ignore empty queries

    const newMessage: Message = { query, answer: '...' };
    const newLoadingIndex = result.length;

    setResult((prevResult) => [...prevResult, newMessage]);
    setLoadingIndex(newLoadingIndex);

    setQuery('');

    const response = await fetch('get-info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (response.ok) {
      const data = await response.json();
      setResult((prevResult) =>
        prevResult.map((message, index) =>
          index === newLoadingIndex ? { ...message, answer: data.answer } : message
        )
      );
      setLoadingIndex(null);
    } else {
      console.error('Request failed');
    }
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event as FormEvent);
    }
  };

  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [result]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return (
    <div className="container mx-auto p-4 flex flex-col min-h-screen">
      <div className="flex gap-2 mb-4">
        <h1 className="font-normal lg:font-semibold">txt to pynecone. </h1>
        <p className="hidden lg:block">ask your uploaded doc(s) some questions.</p>
      </div>

      <div className="flex-1 overflow-auto bg-gray-100 p-4 mb-4">
        <div className="message-container" ref={messageContainerRef}>
          {result.map((message, index) => (
            <div key={index} className="message bg-white rounded shadow-lg p-4 mb-4">
              <div className="query bg-gray-200 rounded p-2 mb-2">
                <div className="query-content">{message.query}</div>
              </div>
              <div className="response bg-white rounded p-2">
                <div className="response-content">
                  {message.answer || (loadingIndex === index && '...')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="fixed bottom-0 left-0 w-full input-container border-b-4 rounded shadow w-full flex justify-center">
      <div className="w-1/2 bg-white input-container border-b-4 rounded shadow">
        <form onSubmit={handleSubmit} className="bg-white input-form flex items-center p-4">
          <textarea
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="ask me something"
            rows={1}
            className="input-field resize-none flex-1 focus:outline-none overflow-auto bg-white"
          />
          <button
            className="submit-button bg-white hover:bg-gray-100 text-gray-800 font-semibold py-2 px-4 border-b-4 bg-white rounded shadow"
            type="submit"
          >
            Submit
          </button>
        </form>
      </div>
    </div>
    </div>
  );
}

export default ChatBot;