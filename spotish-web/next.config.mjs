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
    PLAYER_PORT : process.env.PLAYER_PORT,
    HOST_PLAYER : process.env.HOST_PLAYER,
    CONTROLLER_PORT : process.env.CONTROLLER_PORT,
    HOST_CONTROLLER : process.env.HOST_CONTROLLER,
  },
  images: {
    domains : ["avatars.githubusercontent.com"],
  },
  output : "standalone"
};

export default nextConfig;
