import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import GPTChat from './pages/GPTChat';
export default function App() { 
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/gpt" element={<GPTChat />} />
    </Routes>
  ); 
}
