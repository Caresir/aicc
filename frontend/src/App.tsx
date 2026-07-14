import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Leads from './pages/Leads'
import Agents from './pages/Agents'
import Tasks from './pages/Tasks'
import RealEstate from './pages/RealEstate'
import GymnastDiva from './pages/GymnastDiva'
import FBA from './pages/FBA'
import ContentCalendar from './pages/ContentCalendar'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/real-estate" element={<RealEstate />} />
        <Route path="/gymnast-diva" element={<GymnastDiva />} />
        <Route path="/fba" element={<FBA />} />
        <Route path="/leads" element={<Leads />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/content-calendar" element={<ContentCalendar />} />
      </Route>
    </Routes>
  )
}
