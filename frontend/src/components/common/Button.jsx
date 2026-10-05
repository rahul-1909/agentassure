import React from 'react';

const VARIANTS = {
  primary: 'bg-[#0066FF] hover:bg-[#0052CC] text-white shadow-sm border border-transparent',
  secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200',
  outline: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-sm',
  danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-sm border border-transparent',
  ghost: 'bg-transparent hover:bg-slate-100 text-slate-600',
};

const SIZES = {
  sm: 'px-2.5 py-1.5 text-xs',
  md: 'px-3.5 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
};

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  className = '',
  icon: Icon,
  type = 'button',
}) {
  const variantClass = VARIANTS[variant] || VARIANTS.primary;
  const sizeClass = SIZES[size] || SIZES.md;

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#0066FF]/40 disabled:opacity-50 disabled:cursor-not-allowed ${variantClass} ${sizeClass} ${className}`}
    >
      {Icon && <Icon className={`mr-1.5 ${size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'}`} />}
      {children}
    </button>
  );
}
