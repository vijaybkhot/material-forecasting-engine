# -------- Stage 1: Builder --------
FROM node:18-alpine AS builder
WORKDIR /app

RUN rm -rf node_modules

# Ensure deterministic installs (install devDependencies in builder stage)
ENV NEXT_TELEMETRY_DISABLED=1

# Accept API URL at build time so Next.js can bake it into the bundle
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Install build dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build Next.js (produces .next)
RUN npm run build

# -------- Stage 2: Runtime / Production --------
FROM node:18-alpine AS runner
WORKDIR /app

# Environment for production runtime
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy only needed files
COPY --from=builder /app/package*.json ./
# Install only production dependencies (omit dev)
RUN npm ci --omit=dev

# Copy build output and public assets
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
# If you have custom Next config at runtime (e.g., next.config.js), copy it:
COPY --from=builder /app/next.config.* ./

# Optional: add a non-root user
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs
USER nextjs

EXPOSE 3000
# Healthcheck (optional; endpoint must exist)
# HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
#   CMD wget -qO- http://localhost:3000 || exit 1

# Start production server
CMD ["npm", "start"]
