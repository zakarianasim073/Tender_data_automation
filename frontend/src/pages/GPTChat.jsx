import { useState } from 'react';
import { api } from '../api/client';
export default function GPTChat() {
  const [msg, setMsg] = useState('');
  const [lang, setLang] = useState('en');
  const [history, setHistory] = useState([]);
  const send = async () => {
    if(!msg) return;
    const newMsg = {role:'user', content:msg};
    setHistory(p=>[...p, newMsg]);
    try {
      const r = await api.post('/api/gpt/chat', { messages: [...history, newMsg], language: lang });
      setHistory(p=>[...p, {role:'assistant', content:r.content}]);
    } catch(e) {
      setHistory(p=>[...p, {role:'assistant', content:`❌ ${e.message}`}]);
    }
    setMsg('');
  };
  return (
    <div className="h-screen flex flex-col max-w-2xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">🤖 GPT-4 Tender Assistant</h1>
        <select value={lang} onChange={e=>setLang(e.target.value)} className="border rounded p-1">
          <option value="en">English</option>
          <option value="bn">বাংলা</option>
        </select>
      </div>
      <div className="flex-1 overflow-y-auto border rounded p-4 space-y-3 mb-4 bg-white">
        {history.map((h,i) => <div key={i} className={`p-2 rounded ${h.role==='user'?'bg-blue-100 ml-auto max-w-[80%]':'bg-gray-100 mr-auto max-w-[80%]'}`}>{h.content}</div>)}
      </div>
      <div className="flex gap-2">
        <input className="flex-1 border rounded p-2" value={msg} onChange={e=>setMsg(e.target.value)} onKeyDown={e=>e.key==='Enter' && send()} placeholder={lang==='bn'?'প্রশ্ন লিখুন...':'Type question...'} />
        <button onClick={send} className="bg-blue-600 text-white px-4 rounded">Send</button>
      </div>
    </div>
  );
}
