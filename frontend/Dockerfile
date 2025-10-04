FROM node:24-slim AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm install

COPY frontend/ .

RUN npm run build



FROM node:24-slim AS production

WORKDIR /app

ENV NODE_ENV=production

COPY --from=build /app/.next ./.next
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]