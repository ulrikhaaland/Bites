import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      colors: {
        card: "hsl(0 0% 100%)",
        "card-foreground": "hsl(222.2 47.4% 11.2%)",
        border: "hsl(214.3 31.8% 91.4%)",
        muted: "hsl(210 40% 96.1%)",
        "muted-foreground": "hsl(215.4 16.3% 46.9%)",
      },
    },
  },
  plugins: [],
};

export default config;
