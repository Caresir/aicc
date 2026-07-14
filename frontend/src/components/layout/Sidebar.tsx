import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Users, Bot, CheckSquare, Home, Zap, Sparkles, Package, CalendarDays } from 'lucide-react'
import { cn } from '../../lib/utils'

const NAV = [
  { to: '/',                  label: 'Dashboard',       icon: LayoutDashboard },
  { to: '/real-estate',       label: 'Real Estate',     icon: Home },
  { to: '/content-calendar',  label: 'Content Calendar',icon: CalendarDays },
  { to: '/gymnast-diva',      label: 'GymnastDiva',     icon: Sparkles },
  { to: '/fba',               label: 'Amazon FBA',      icon: Package },
  { to: '/leads',             label: 'Leads',           icon: Users },
  { to: '/agents',            label: 'Agents',          icon: Bot },
  { to: '/tasks',             label: 'Tasks',           icon: CheckSquare },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-stone-900 border-r border-stone-800 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-stone-800">
        <div className="flex items-center gap-2">
          <Zap className="text-emerald-500" size={20} />
          <span className="font-heading font-bold text-sm text-stone-100 leading-tight">
            Locked In<br />
            <span className="text-emerald-500">with Kareesa</span>
          </span>
        </div>
        <p className="text-stone-500 text-xs mt-1">AI Command Center</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-emerald-600/20 text-emerald-400 font-semibold'
                  : 'text-stone-400 hover:text-stone-100 hover:bg-stone-800'
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-stone-800">
        <p className="text-stone-600 text-xs">KW Preferred · Pearland TX</p>
      </div>
    </aside>
  )
}
