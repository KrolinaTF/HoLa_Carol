import React, { useState } from 'react';
import QueryForm from './components/QueryForm';
import ResponseDisplay from './components/ResponseDisplay';

function App() {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (queryData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/medical/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer your-token-here' // Necesitarás implementar la autenticación
        },
        body: JSON.stringify({
          query: queryData.query,
          user_id: "test-user", // Esto deberá venir de tu sistema de autenticación
          context: {}
        })
      });

      if (!response.ok) {
        throw new Error('Error en la consulta');
      }

      const data = await response.json();
      setResponse(data);
    } catch (error) {
      setError('Error procesando tu consulta. Por favor, intenta de nuevo.');
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <QueryForm onSubmit={handleSubmit} isLoading={isLoading} />
      
      {error && (
        <div className="max-w-3xl mx-auto mt-4 p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}
      
      {response && <ResponseDisplay response={response} />}
    </div>
  );
}

export default App;