import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
}

export const Card: React.FC<CardProps> = ({ title, subtitle, children, className = '', ...rest }) => {
  return (
    <section
      className={`bg-white border border-slate-200 rounded-card shadow-sm p-5 ${className}`}
      {...rest}
    >
      {(title || subtitle) && (
        <header className="mb-3">
          {title && <h2 className="text-base font-semibold text-slate-900">{title}</h2>}
          {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
        </header>
      )}
      {children}
    </section>
  );
};
