# ---------- STAGE 1: build ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Brži build cache
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
# koristi npm ci ako imaš package-lock.json, pnpm/yarn ako koristiš njih
RUN if [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
    elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    else npm i; fi

# Kopiraj ostatak i izgradi
COPY . .
RUN npm run build

# ---------- STAGE 2: serve ----------
FROM nginx:alpine
# kopiraj build output
COPY --from=builder /app/dist /usr/share/nginx/html
# tvoj Nginx proxy config (ispravno ime i putanja!)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1
CMD ["nginx", "-g", "daemon off;"]
