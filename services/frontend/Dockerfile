# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:18 as build-stage

ARG ENVIRONMENT=production

RUN mkdir /carlos
WORKDIR /carlos

# install all requirements of the FE
COPY .yarn/ /carlos/
COPY yarn.lock /carlos/
COPY package*.json /carlos/
COPY ./services/frontend/package*.json /carlos/services/frontend/

RUN yarn set version classic
RUN yarn install --immutable

# at last copy all code to utilize caching of docker layers
COPY ./services/frontend /carlos/services/frontend
# Copy the branding folder, as it contains targets for symbolic links
COPY ./branding /carlos/branding

ENV NODE_ENV=$ENVIRONMENT
RUN yarn run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

COPY --from=build-stage /carlos/services/frontend/entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY --from=build-stage /carlos/services/frontend/nginx.conf /etc/nginx/conf.d/default.conf

RUN rm -rf ./*
COPY --from=build-stage /carlos/services/frontend/dist ./

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
