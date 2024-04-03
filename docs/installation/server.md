# Carlos Server (Linux)

This guide will explain how to setup a fresh Debian 12 server.
But you are free to use any other Linux distribution or even a Windows server.
But keep in mind that the commands and paths may differ.

To keep the maintenance effort minimal we only require and rely on: `git`, `docker` (`docker-compose`) and `cron`.
`git` is used to clone the carlos repository and therefore allow us to update the server easily.
`docker` and `docker-compose` are used to run the carlos server without the need to install any dependencies on the host system.
`cron` is used to automatically renew the SSL certificates.

We install all tools by running the following commands:
 
```bash
sudo apt update && sudo apt install git docker.io docker-compose cron
```

Now you are ready to clone the carlos repository in the root of your server.
_If you decide to clone the repository in a different directory, make sure to adjust the paths in the `docker-compose.yml` files as well as all follwing scripts._

```bash
cd / && git clone https://github.com/flxdot/carlos.git
```

Before we can start the carlos server we need to create a `.env` file in the root of the repository.

```bash
cd /carlos && cp .env.example .env
```

Now you need to adjust the `.env` file to your needs.

```bash
sh /carlos/deployment/server/install.sh your-domain.com your-email@provider.com
```
