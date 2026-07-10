# Raw-Socket Architecture: In-Memory DB & HTTP Server
 
![Python](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-gevent-orange)
 
A zero-dependency, multi-process backend infrastructure engineered entirely from scratch in Python. This project demonstrates core networking concepts, memory isolation, raw TCP socket management, and manual HTTP protocol parsing without relying on external web frameworks.
 
## Table of Contents
 
- [System Architecture](#system-architecture)
- [Components](#components)
- [Design Philosophy](#design-philosophy)
- [Installation](#installation--requirements)
- [Execution Pipeline](#execution-pipeline)
- [API Reference](#api-reference--testing)
- [Static Asset Delivery](#static-asset-delivery)
- [Known Limitations](#known-limitations)
- [License](#license)
## System Architecture
 
The infrastructure operates on a distributed, two-node microservice model to ensure strict resource isolation and fault tolerance.
 
```
                        Client
                          |
                HTTP requests (port 8080)
                          v
              +----------------------------+
              |         BOUNCER            |
              |     (server.py — API)      |
              |----------------------------|
              |  request parsing           |
              |  static file routing       |
              |  request → command mapping |
              +----------------------------+
                          |
       Custom binary protocol via tcp port(port 31337)
                          v
              +----------------------------+
              |          VAULT             |
              |    (main.py — storage)     |
              |----------------------------|
              |  in-memory key/value store |
              |  gevent worker pool        |
              +----------------------------+
```
 
Two independently runnable processes, one API contract between them. The Bouncer never touches storage directly, and the Vault never speaks HTTP, same pattern you'd see in a service that talks to Redis or a database over its own wire protocol.
 
## Components
 
### 1. The Bouncer (HTTP Edge Server)
 
- **Protocol:** HTTP/1.0 via TCP (Port 8080)
- **Function:** A stateless edge server that intercepts raw internet traffic. It manually decodes HTTP headers, handles static file routing (`/index.html`), and acts as an API gateway. It safely parses `GET` and `POST` payloads and bridges them to the internal database.
- **Resilience:** Designed to absorb malformed web traffic and isolate HTTP connection exhaustion from the application state.
### 2. The Vault (Key-Value Store)
 
- **Protocol:** Custom binary protocol via TCP (Port 31337)
- **Function:** A stateful, Redis-inspired in-memory database. It uses a custom protocol handler to read raw byte streams, serialize/deserialize data safely, and maintain application state in RAM.
- **Resilience:** Runs as a completely isolated process. If the edge server crashes under load, the data in the Vault remains secure and instantly accessible upon edge recovery.
## Design Philosophy
 
I built this to understand what frameworks like FastAPI or Express are actually doing behind the scenes, parsing requests, managing connections, routing data, instead of just importing them and trusting the magic.
 
A few things I focused on:
 
- **Splitting the API from the storage.** The Bouncer only handles HTTP requests. The Vault only handles storing and retrieving data. They talk to each other over a simple protocol on port 31337, but neither one needs to know how the other actually works internally. This is basically the same idea as separating your API server from your database in a real app, just done manually here so I could see how that connection actually works.
- **Keeping them as separate processes on purpose.** If the Bouncer crashes or gets overloaded with bad requests, the Vault and the data inside it are unaffected. This mirrors why real backend systems often run their API and their database/cache as separate services instead of one big process.
- **Parsing things by hand to actually learn it.** Writing my own HTTP parsing and my own protocol for the Vault meant running into problems frameworks normally hide from you — like partial messages, bad input, and edge cases in encoding. It was slower to build, but I understood every part of it by the end.
- **Kept it simple on purpose.** The Vault is just an in-memory key/value store, not a real database, no persistence, no authentication, no advanced concurrency handling. I focused first on getting the request/response flow and the process separation right. The next steps I'd want to add are listed in [Known Limitations](#known-limitations).

## Installation & Requirements
 
This project relies purely on Python's standard library and the `gevent` networking library for asynchronous I/O.
 
```bash
# Clone the repository
git clone https://github.com/cezium55/rediis-clone-own.git
cd rediis-clone-own
 
# Install the networking dependency
pip install -r requirements.txt
```
 
## Execution Pipeline
 
Due to the microservice architecture, **the Vault must be initialized before the Edge Server** to establish the API bridge.
 
**Terminal 1 — Boot the Vault**
 
```bash
python main.py
# Output: Starting server on 127.0.0.1:31337...
```
 
**Terminal 2 — Boot the Bouncer**
 
```bash
python server.py
# Output: Bouncer listening on port 8080 ...
```
 
## API Reference & Testing
 
You can interact with the live infrastructure using standard `curl` commands in a third terminal window.
 
### Read State (`GET`)
 
Validates the connection bridge and retrieves the current server status from memory.
 
```bash
curl http://127.0.0.1:8080/api/status
```
 
**Response:** `HTTP 200 OK`
 
```
ByteCache Vault is Online!
```
 
### Mutate State (`POST`)
 
Injects a payload into the edge server, which parses the string and writes it permanently to the Vault's memory.
 
```bash
curl -X POST http://127.0.0.1:8080/api/save -d "status=system_override_active"
```
 
**Response:** `HTTP 200 OK`
 
```
Data successfully secured in ByteCache Vault!
```
 
## Static Asset Delivery
 
The server acts as a standard file host for the `/frontend` directory.
 
```bash
curl http://127.0.0.1:8080/index.html
```
 
## Known Limitations
 
This is an educational / demonstration project, not a production-hardened service. Notable gaps:
 
- No TLS, traffic between client and Bouncer, and between Bouncer and Vault, is unencrypted.
- HTTP/1.0 only, no keep-alive, no chunked transfer encoding, no HTTP/1.1+ features.
- No authentication on the Vault's binary protocol port; anything that can reach 31337 can read/write state.
- No persistence, all data lives in RAM and is lost on Vault restart.
- Minimal input validation beyond basic parsing; not hardened against adversarial payloads.
## License
 
This project is licensed under the MIT License, see the [LICENSE](LICENSE) file for details.
