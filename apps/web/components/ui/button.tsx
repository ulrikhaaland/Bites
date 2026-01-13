import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium transition",
        variant === "primary"
          ? "bg-slate-900 text-white hover:bg-slate-800"
          : "bg-transparent text-slate-700 hover:bg-slate-100",
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";

export { Button };
