import { useState } from 'react';
import { api } from '../api/client';
export default function Dashboard() {
  const [boq, setBoq] = useState('');
  const [sor, setSor] = useState('');
  const [res, setRes] = useState(null);
  const handleDiff = async () => {
    try { 
      const r = await api.post('/api/boq/diff', { boq: JSON.parse(boq), sor: JSON.parse(sor) }); 
      setRes(r); 
    } catch(e) { 
      setRes({error: e.message}); 
    }
  };
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">🏗 BOQ AI Dashboard</h1>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <textarea className="border p-2 rounded h-32" placeholder='BOQ JSON: [{"item":"Cement","rate":500}]' onChange={e=>setBoq(e.target.value)} />
        <textarea className="border p-2 rounded h-32" placeholder='SOR JSON: [{"item":"Cement","rate":480}]' onChange={e=>setSor(e.target.value)} />
      </div>
      <button onClick={handleDiff} className="bg-blue-600 text-white px-4 py-2 rounded">Run Diff</button>
      {res && <pre className="mt-4 bg-gray-900 text-green-400 p-4 rounded overflow-auto">{JSON.stringify(res, null, 2)}</pre>}
    </div>
  );
}
