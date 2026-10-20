import React from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';

export const DashboardLayout: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('psx_token');
    navigate('/login');
  };

  const navItemClasses = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium border border-transparent ${
      isActive
        ? 'bg-primary text-white border-primary'
        : 'text-muted hover:bg-slate-50 hover:border-slate-200'
    }`;

  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-semibold text-primary">
            PSXviewAI
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink to="/" className={navItemClasses} end>
              Dashboard
            </NavLink>
            <NavLink to="/companies" className={navItemClasses}>
              Companies
            </NavLink>
            <NavLink to="/news" className={navItemClasses}>
              News
            </NavLink>
            <NavLink to="/assistant" className={navItemClasses}>
              Assistant
            </NavLink>
            <button
              type="button"
              onClick={handleLogout}
              className="ml-4 px-3 py-2 text-sm text-muted border border-slate-200 rounded-md hover:bg-slate-50"
            >
              Log out
            </button>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
};
