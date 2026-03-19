FROM node:20-alpine

WORKDIR /app

ENV CI=true

RUN corepack enable

COPY package.json /app/package.json
RUN pnpm install

COPY . /app

EXPOSE 5000

CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "5000"]
