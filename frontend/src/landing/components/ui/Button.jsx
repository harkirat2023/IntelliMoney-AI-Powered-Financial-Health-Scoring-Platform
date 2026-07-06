import { forwardRef } from "react";
import { Link } from "react-router-dom";

const variants = {
  primary:
    "bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-600/25 hover:shadow-emerald-600/40",
  secondary:
    "bg-white text-neutral-900 border border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50 shadow-sm",
  ghost:
    "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100",
  outline:
    "bg-transparent text-emerald-600 border border-emerald-600 hover:bg-emerald-50",
  gradient:
    "gradient-cta text-white shadow-lg shadow-emerald-600/30 hover:shadow-emerald-600/50",
};

const sizes = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-5 py-2.5 text-sm",
  lg: "px-7 py-3 text-base",
  xl: "px-8 py-3.5 text-base",
};

export const Button = forwardRef(
  ({ variant = "primary", size = "md", href, children, className = "", icon: Icon, ...props }, ref) => {
    const base = "inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]";
    const cls = `${base} ${variants[variant]} ${sizes[size]} ${className}`;

    if (href) {
      return (
        <Link to={href} className={cls} ref={ref}>
          {Icon && <Icon size={18} />}
          {children}
        </Link>
      );
    }
    return (
      <button className={cls} ref={ref} {...props}>
        {Icon && <Icon size={18} />}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
