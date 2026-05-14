FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --include=dev

FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-bookworm-slim AS run
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000
RUN groupadd -g 10001 keyhan && useradd -u 10001 -g 10001 -m keyhan
COPY --from=build --chown=keyhan:keyhan /app/.next/standalone ./
COPY --from=build --chown=keyhan:keyhan /app/.next/static ./.next/static
COPY --from=build --chown=keyhan:keyhan /app/public ./public
USER keyhan
EXPOSE 3000
CMD ["node", "server.js"]
