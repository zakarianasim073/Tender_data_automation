export const api = {
  post: async (url, body) => {
    const baseUrl = 'https://boq-ai-backend-service.onrender.com';
    const targetUrl = url.startsWith('http') ? url : baseUrl + url;
    const res = await fetch(targetUrl, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    if(!res.ok) throw new Error((await res.json()).detail || 'API Error');
    return res.json();
  }
};
