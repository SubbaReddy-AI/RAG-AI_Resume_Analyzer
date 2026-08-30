FROM nginx:alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend files
COPY . /usr/share/nginx/html/

# Nginx listens on port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]