FROM node:20 AS build

ARG VUE_APP_API_URL=https://api.vinegrape.ru
ENV VUE_APP_API_URL=$VUE_APP_API_URL

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
