import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import crypto from 'crypto';

export default defineConfig({
  plugins: [
    vue({
      template: {
        transformAssetUrls: {
          includeAbsolute: false,
        },
      },
    }),
  ],
  build: {
    lib: {
      entry: {
        liv: 'src/app.js',
      },
      name: 'LIV',
      formats: ['umd'],
    },
    rollupOptions: {
      output: {
        entryFileNames: `[name].js`,
        chunkFileNames: `[name].js`,
        assetFileNames: `[name].[ext]`,
      },
    },
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
  },
  css: {
    modules: {
      generateScopedName: (name, filename, css) => {
        let componentName;
        // prefer using the component name, but fall back to hash if that
        // doesn't work
        try {
          componentName = filename.split('/').pop().split('.')[0].toLowerCase();
        } catch {
          componentName = crypto
            .createHash('md5')
            .update(css)
            .digest('base64')
            .substring(0, 5);
        }
        return `liv_${componentName}__${name}`;
      },
    },
  },
});
