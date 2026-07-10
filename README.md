## Raw-Socket Architecture: In-Memory DB & HTTP Server
A zero-dependency, multi-process backend infrastructure engineered entirely from scratch in Python. This project demonstrates core networking concepts, memory isolation, raw TCP socket management, and manual HTTP protocol parsing without relying on external abstractions or web frameworks.

## System Architecture

The infrastructure operates on a distributed, two-node microservice model to ensure strict resource isolation and fault tolerance.

```text
       [ Internet / Client ]
                 |
                 | HTTP/1.0 via TCP (Port 8080)
                 v
      +-------------------------+
      |       THE BOUNCER       |
      |   (server.py / Web)     |
      |                         |
      | - Parses HTTP Headers   |
      | - Static File Routing   |
      | - API Gateway Logic     |
      +-------------------------+
                 |
                 | Custom Binary Protocol via TCP 
                 | Port 31337 (The API Bridge)
                 v
      +-------------------------+
      |        THE VAULT        |
      |  (main.py / Database)   |
      |                         |
      | - gevent Async Pool     |
      | - In-Memory RAM Store   |
      | - Key/Value Execution   |
      +-------------------------+

1. The Bouncer (HTTP Edge Server)
Protocol: HTTP/1.0 via TCP (Port 8080)

Function: A stateless edge server that intercepts raw internet traffic. It manually decodes HTTP headers, handles static file routing (/index.html), and acts as an API gateway. It safely parses GET and POST payloads and bridges them to the internal database.

Resilience: Designed to absorb malformed web traffic and isolate HTTP connection exhaustion from the application state.

2. The Vault (Key-Value Store)
Protocol: Custom Binary Protocol via TCP (Port 31337)

Function: A stateful, Redis-inspired in-memory database. It utilizes a custom protocol handler to read raw byte streams, serialize/deserialize data safely, and maintain the application state in RAM.

Resilience: Runs as a completely isolated process. If the edge server crashes under load, the data in the Vault remains completely secure and instantly accessible upon edge recovery.

Design Philosophy
This project was built to demonstrate a fundamental understanding of OSI Layers 4 through 7. Rather than using industry-standard frameworks (like FastAPI or Express) to abstract away the network layer, this architecture handles socket bindings, byte-decoding, and HTTP framing directly at the operating system level.

Installation & Requirements
This project relies purely on Python's standard library and the gevent networking library for asynchronous I/O.

Bash
# Clone the repository
git clone https://github.com/yourusername/rediis-clone-own.git
cd rediis-clone-own

# Install the networking dependency
pip install -r requirements.txt
Execution Pipeline
Due to the microservice architecture, the Vault must be initialized before the Edge Server to establish the API bridge.

Terminal 1: Boot the Vault

Bash
python main.py
# System will output: Starting server on 127.0.0.1:31337...
Terminal 2: Boot the Bouncer

Bash
python server.py
# System will output: Bouncer listening on port 8080 ...
API Reference & Testing
You can interact with the live infrastructure using standard curl commands in a third terminal window.

Read State (GET)
Validates the connection bridge and retrieves the current server status from memory.

Bash
curl http://127.0.0.1:8080/api/status
Response: HTTP 200 OK

Plaintext
ByteCache Vault is Online!
Mutate State (POST)
Injects a payload into the edge server, which parses the string and writes it permanently to the Vault's memory.

Bash
curl -X POST http://127.0.0.1:8080/api/save -d "status=system_override_active"
Response: HTTP 200 OK

Plaintext
Data successfully secured in ByteCache Vault!
Static Asset Delivery
The server acts as a standard file host for the /frontend directory.

Bash
curl http://127.0.0.1:8080/index.html
License
This project is licensed under the MIT License - see the LICENSE file for details.

