import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
    build: {
      sourcemap: true,
    },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Maps "@" to "src" folder
    },
  },
});
