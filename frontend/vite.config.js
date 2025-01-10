import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
    dedupe: ['@emotion/react', '@emotion/styled']
  },
  optimizeDeps: {
    include: ['@emotion/react', '@emotion/styled'],
  },
  build: {
    commonjsOptions: {
      include: [/node_modules/, /@emotion\/react/, /@emotion\/styled/],
    },
    outDir: 'build',
    sourcemap: true,
    rollupOptions: {
      external: ['@emotion/react', '@emotion/styled'],
      onwarn(warning, warn) {
        if (warning.code === 'MODULE_LEVEL_DIRECTIVE' && warning.message.includes('use client')) {
          return;
        }
        warn(warning);
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});