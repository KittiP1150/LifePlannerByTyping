const API_BASE_URL = 'http://localhost:8000/api/v1';

export const getTasksByDate = async (targetDate) => {
  const response = await fetch(`${API_BASE_URL}/plan?target_date=${targetDate}`);
  if (!response.ok) throw new Error('Failed to fetch tasks');
  return response.json();
};

export const sendChatToBackend = async (message, targetDate) => {
  const userApiKey = localStorage.getItem('GROQ_API_KEY');

  if (!userApiKey) {
    alert("Need GROQ API Key");
    throw new Error('API Key is missing');
  }

  const response = await fetch(`${API_BASE_URL}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json',
      'X-API-Key': userApiKey
     },
    body: JSON.stringify({ 
      user_message: message,
      target_date: targetDate
     })
  });
  
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};