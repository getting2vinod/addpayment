# Use the official NGINX image from Docker Hub
FROM nginx:alpine

# Copy the custom NGINX configuration file to the container
COPY conf/nginx.conf /etc/nginx/nginx.conf
#Generate the crt, key and dhparam using the below link
#https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-20-04-1

# Copy the HTML file to the NGINX web directory
COPY index.html /usr/share/nginx/html/index.html
COPY dhparam.pem /etc/ssl/certs/dhparam.pem
COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY ssl-params.conf /etc/nginx/snippets/ssl-params.conf

# Expose port 80 for web traffic
EXPOSE 80

# Start NGINX when the container starts
CMD ["nginx", "-g", "daemon off;"]