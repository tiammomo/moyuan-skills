import type { Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        paper: 'var(--paper)',
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        line: 'var(--line)',
        accent: 'var(--accent)',
        'accent-soft': 'var(--accent-soft)',
        olive: 'var(--olive)',
      },
      boxShadow: {
        card: 'var(--shadow)',
      },
      borderRadius: {
        card: '20px',
        'card-lg': '24px',
        'card-xl': '28px',
      },
      fontFamily: {
        sans: ['"Segoe UI"', '"PingFang SC"', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config;
