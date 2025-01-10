import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      'styled-components': path.resolve(__dirname, 'node_modules', 'styled-components')
    },
    dedupe: ['styled-components']  // Add deduplication for framer-motion
  },
  build: {
    outDir: 'build',
    sourcemap: true,
    rollupOptions: {
        external: ['styled-components'],  // Changed from framer-motion to motion
        onwarn(warning, warn) {
            if (warning.code === 'MODULE_LEVEL_DIRECTIVE' && 
                warning.message.includes('use client')) {
                return;
            }
            warn(warning);
        },
    },
  },
  optimizeDeps: {
    include: ['styled-components']  // Include framer-motion in dependency optimization
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