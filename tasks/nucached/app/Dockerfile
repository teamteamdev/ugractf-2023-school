FROM node:alpine
WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm ci && chown -R root:root node_modules
USER node:node
COPY . ./
CMD ["node", "."]
