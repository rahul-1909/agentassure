import React from 'react';

const VARIANT_STYLES = {
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  error: 'bg-rose-50 text-rose-700 border-rose-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  info: 'bg-blue-50 text-blue-700 border-blue-200',
  purple: 'bg-purple-50 text-purple-700 border-purple-200',
  pink: 'bg-pink-50 text-pink-700 border-pink-200',
  neutral: 'bg-slate-100 text-slate-700 border-slate-200',
};

export default function Badge({ children, variant = 'neutral', className = '' }) {
  const style = VARIANT_STYLES[variant] || VARIANT_STYLES.neutral;
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${style} ${className}`}
    >
      {children}
    </span>
  );
}
