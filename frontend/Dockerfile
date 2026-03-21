# ---------- build ----------
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# L'URL de l'API est injectée au build (Vite l'inline dans le bundle)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# ---------- serve ----------
FROM nginx:1.27-alpine

# Copier le build statique
COPY --from=build /app/dist /usr/share/nginx/html

# Config Nginx pour SPA (react-router-dom : toutes les routes → index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
