# this file is used to build the docker image for the api_proxy
# it should be built with the context set to the root of the project
FROM nginx:mainline

# Links Docker image with repository
LABEL org.opencontainers.image.source=https://github.com/0x6f677548/fastapi-bootstrap



#create a backup of the original config files
RUN cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
RUN cp /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak

#remove the original config files as we will be using our own
RUN rm /etc/nginx/conf.d/default.conf /etc/nginx/nginx.conf


# ---- Copy the config files ----
#nginx config file
COPY ./docker/api_proxy/config/nginx.conf /etc/nginx/nginx.conf

#copy conf.d directory and all files in it
COPY ./docker/api_proxy/config/conf.d/ /etc/nginx/conf.d

#copy the cloudflare ips file
COPY ./docker/api_proxy/config/cloudflare_ips.conf /etc/nginx/cloudflare_ips.conf