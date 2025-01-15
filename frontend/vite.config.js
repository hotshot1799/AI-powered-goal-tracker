import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    dedupe: ['@emotion/react', '@emotion/styled'],
  },
  optimizeDeps: {
    include: ['@emotion/react', '@emotion/styled'],
  },
  build: {
    outDir: 'build',
    sourcemap: true,
    rollupOptions: {
      external: ['styled-components'],
      onwarn(warning, warn) {
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE' && warning.message.includes('use client')) {
          return;
        }
        warn(warning);
      },
    },
  },
  server: {
    port: 5173,
    strictPort: true
  },
});