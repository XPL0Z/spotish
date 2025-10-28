import path from 'path';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Chemin absolu vers le fichier .env
const envPath = path.resolve(__dirname, '../.env');
console.log('Chemin du .env:', envPath);

// Charger les variables d'environnement
config({ path: envPath });

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    CLIENT_ID: process.env.CLIENT_ID,
    CLIENT_SECRET: process.env.CLIENT_SECRET,
  },
};

export default nextConfig;
