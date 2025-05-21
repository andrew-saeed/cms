import path from 'path'
import { defineConfig, splitVendorChunkPlugin } from 'vite'
import tailwindcss from '@tailwindcss/vite'

const ROOT = path.resolve('')
const BASE = __dirname.replace(ROOT, '')

export default defineConfig({
    base: BASE,
    server: {
        port: 4200
    },
    build: {
        manifest: 'manifest.json',
        assetsDir: '.',
        outDir: `../static`,
        emptyOutDir: true,
        sourcemap: false,
        rollupOptions: {
            input: [
                'src/main.js',
                'src/style.css',
            ],
            output: {
                entryFileNames: '[hash].js',
                assetFileNames: '[hash].[ext]',
                chunkFileNames: '[name].[hash].js',
                manualChunks(id) {
                    if (id.includes('node_modules')) return 'vendor'
                },
            }
        },
    },
    plugins: [
        tailwindcss(),
        {
            name: 'py',
            handleHotUpdate({ file, server }) {
                if (file.endsWith('.html')) {
                    server.ws.send({ type: 'full-reload' });
                }
            }
        },
    ],
})