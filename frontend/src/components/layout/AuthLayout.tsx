import React from 'react';
import { Outlet, Link } from 'react-router-dom';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="w-full max-w-md bg-white border border-slate-200 rounded-card shadow-sm p-8">
        <Link to="/" className="block mb-6 text-center text-2xl font-semibold text-primary">
          PSXviewAI
        </Link>
        <Outlet />
      </div>
    </div>
  );
};
