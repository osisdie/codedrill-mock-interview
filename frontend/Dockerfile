FROM node:22-slim

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json ./
RUN pnpm install

COPY . .

EXPOSE 5173

CMD ["pnpm", "dev"]
