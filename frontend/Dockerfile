# Base stage with pnpm
FROM node:18-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

# Add necessary build tools
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Development stage
FROM base AS development

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install all dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Expose port for development
EXPOSE 3000

# Set environment for development
ENV NODE_ENV=development
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

# Health check for development
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Development command
CMD ["pnpm", "dev"]

# Build stage
FROM base AS builder

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build arguments for environment variables
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_ENVIRONMENT=production

# Set build-time environment variables
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT

# Use Cloud Run specific config if deploying to Cloud Run
RUN if [ -f "next.config.cloudrun.mjs" ]; then \
      mv next.config.cloudrun.mjs next.config.mjs; \
    fi

# Build the application
RUN pnpm build

# Production stage
FROM node:18-alpine AS runner

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.11.0 --activate

WORKDIR /app

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy built application
COPY --from=builder /app/package.json ./
COPY --from=builder /app/pnpm-lock.yaml ./
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Install only production dependencies
RUN pnpm install --prod --frozen-lockfile

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 8080

# Set environment variable for Cloud Run
ENV PORT 8080
ENV NODE_ENV production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD node -e "require('http').get('http://localhost:${PORT:-8080}/api/health', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Start the application
CMD ["node", "server.js"]