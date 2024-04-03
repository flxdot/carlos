# Carlos Server (Linux)

This guide will explain how to setup a fresh Debian 12 server.
But you are free to use any other Linux distribution or even a Windows server.
But keep in mind that the commands and paths may differ.

To keep the maintenance effort minimal we only require and rely on:

- `git` is used to clone the carlos repository and therefore allow us to update the server easily.
- `docker` and `docker-compose` are used to run the carlos server without the need to install any dependencies on the host system.
- `cron` is used to automatically renew the SSL certificates.
- `ufw` is used to manage the firewall and to allow HTTP and HTTPS connections.

We install all tools by running the following commands:
 
```bash
sudo apt update && sudo apt install git docker.io docker-compose cron ufw
```

Next we configure our server to accept HTTP and HTTPS connections.

```bash
sudo ufw allow 80/tcp comment 'accept HTTP connections'
sudo ufw allow 443/tcp comment 'accept HTTPS connections'
```

Now you are ready to clone the carlos repository in the root of your server.
_If you decide to clone the repository in a different directory, make sure to adjust the paths in the `docker-compose.yml` files as well as all follwing scripts._

```bash
git clone https://github.com/flxdot/carlos.git /carlos
```

Before we can start the carlos server we need to provide it with some configuration parameters in the `.env` file in the root of the repository:

```bash
cp /carlos/.env.example /carlos/.env
# edit the .env file with your favorite editor
vi /carlos/.env
```

As a last step we run the installation script that will configure certbot and nginx to serve the carlos server over HTTPS.

```bash
sh /carlos/deployment/server/install.sh your-domain.com your-email@provider.com
```

Your server is now running and you can access it by visiting `https://your-domain.com`.
