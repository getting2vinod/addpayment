# Use the official NGINX image from Docker Hub
FROM nginx:alpine

# Copy the custom NGINX configuration file to the container
COPY conf/nginx.conf /etc/nginx/nginx.conf

# Copy the HTML file to the NGINX web directory
COPY index.html /usr/share/nginx/html/index.html

# Expose port 80 for web traffic
EXPOSE 80

# Start NGINX when the container starts
CMD ["nginx", "-g", "daemon off;"]
