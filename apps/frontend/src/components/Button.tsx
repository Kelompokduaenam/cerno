import type { ButtonHTMLAttributes } from "react";

export const Button = ({ children, className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button className={`button ${className}`} {...props}>{children}</button>
);
