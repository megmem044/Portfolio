# Builds and runs the browser-facing Express server.
FROM node:24-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY src ./src
EXPOSE 3000
CMD ["npm", "start"]
