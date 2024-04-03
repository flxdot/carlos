# Installation

Carlos uses two entities to operate: the **Carlos Server** and the **Carlos Device**.

The **Carlos Server** is a (preferably) Linux machine that runs the main application stack.
This includes the web server, the database, and the API. For an installation guide, see the [Carlos Server (Linux)](server.md) page.

The **Carlos Device** is a (preferably) a Raspberry Pi that collects sensor data from within the greenhouse, sends it to the server, and receives commands from the server to control the greenhouse.
For an installation guide, see the [Carlos Device (Raspberry Pi)](device.md) page.
This project defines a couple of supported sensors and actuators, but you can easily extend the project to support your own devices to provide the required data to the server.

The intended setup is to have the **Carlos Server** deployed in the cloud and the **Carlos Device** running locally in the greenhouse.
But nothing stops you from running the **Carlos Server** on a Raspberry Pi as well if you have access to the Raspberry Pi within your home network.
