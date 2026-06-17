import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEnv } from 'vite';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const mode = process.env.NODE_ENV === 'production' ? 'production' : 'development';
const env = loadEnv(mode, root, '');

const templatePath = resolve(root, 'public/firebase-messaging-sw.template.js');
const outputPath = resolve(root, 'public/firebase-messaging-sw.js');

const template = readFileSync(templatePath, 'utf8');

const values = {
  FIREBASE_API_KEY: env.VITE_FIREBASE_API_KEY || '',
  FIREBASE_AUTH_DOMAIN: env.VITE_FIREBASE_AUTH_DOMAIN || '',
  FIREBASE_PROJECT_ID: env.VITE_FIREBASE_PROJECT_ID || '',
  FIREBASE_STORAGE_BUCKET: env.VITE_FIREBASE_STORAGE_BUCKET || '',
  FIREBASE_MESSAGING_SENDER_ID: env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  FIREBASE_APP_ID: env.VITE_FIREBASE_APP_ID || '',
};

let output = template;
for (const [key, value] of Object.entries(values)) {
  output = output.replaceAll(`__${key}__`, value);
}

writeFileSync(outputPath, output, 'utf8');
console.log('firebase-messaging-sw.js güncellendi');
