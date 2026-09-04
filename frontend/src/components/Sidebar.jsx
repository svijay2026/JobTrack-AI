import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, Kanban, FileText, Brain, FileSpreadsheet, History, LogOut, User
} from 'lucide-react';

const navItems = [
  { to: '/dashboard', icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
  { to: '/kanban',    icon: <Kanban size={18} />,          label: 'Kanban Board' },
  { to: '/resumes',   icon: <FileText size={18} />,        label: 'Resumes' },
  { to: '/match',     icon: <Brain size={18} />,           label: 'AI Match' },
  { to: '/cover-letter', icon: <FileSpreadsheet size={18} />, label: 'Cover Letter' },
  { to: '/history',   icon: <History size={18} />,         label: 'Match History' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🎯</div>
        <span className="logo-text">JobTrack AI</span>
      </div>

      <nav style={{ flex: 1 }}>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16 }}>
        <div className="nav-item" style={{ cursor: 'default', paddingBottom: 8 }}>
          <User size={18} />
          <span style={{ fontSize: 13, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {user?.full_name || 'User'}
          </span>
        </div>
        <div className="nav-item" onClick={handleLogout} style={{ color: '#f87171' }}>
          <LogOut size={18} />
          <span>Logout</span>
        </div>
      </div>
    </div>
  );
}
