import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import GPTChat from './pages/GPTChat';
import AdminDashboard from './pages/AdminDashboard';
export default function App() { 
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/gpt" element={<GPTChat />} />
          <Route path="/admin" element={<AdminDashboard />} />
    </Routes>
  ); 
}
