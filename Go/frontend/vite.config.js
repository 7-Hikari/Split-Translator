import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'es2022',
    outDir: 'dist', // Memastikan hasil build masuk ke folder frontend/dist
  },
  optimizeDeps: {
    esbuildOptions: {
      target: 'es2022',
    },
  },
});
