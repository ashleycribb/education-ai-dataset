# Proof-of-Concept: MCP Server and Client

This proof-of-concept (PoC) provides a working demonstration of the high-performance MCP (Message-Oriented Communication Protocol) interface described in our [Conceptual Communication Model](../COMMUNICATION_MODEL.md).

It is designed for a **non-technical audience** to help visualize how a dedicated AI agent (the "client") would send data to the AI-Enhanced LRS (the "server") over a fast and direct communication channel.

## What It Does

This PoC consists of two simple Python scripts:

1.  **`server.py`:** This script acts as our LRS. It will start up and wait for a client to connect.
2.  **`client.py`:** This script acts as our AI Teacher's Assistant. It will load a sample xAPI statement, connect to the server, send the data, and wait for a response.

By running these two scripts in separate terminal windows, you can see the communication happen in real time, from the client sending the data to the server receiving and acknowledging it.

## How to Run It

This demonstration requires two terminal windows running at the same time.

### Terminal 1: Start the Server

1.  Open your first terminal or command prompt.
2.  Navigate into this `mcp-poc` directory.
3.  Run the following command to start the server:

    ```bash
    python server.py
    ```

4.  You will see the message `--- MCP Server listening on 127.0.0.1:12345 ---`. The server is now running and waiting for the client to connect.

### Terminal 2: Run the Client

1.  Open a **new** terminal or command prompt (keep the first one running).
2.  Navigate into this `mcp-poc` directory as well.
3.  Run the following command to start the client:

    ```bash
    python client.py
    ```

### Observe the Results

*   In the **client terminal**, you will see the xAPI statement being sent and then a success message from the server.
*   In the **server terminal**, you will see a message confirming that a client has connected, followed by the data it received.

This simple exchange demonstrates the core concept of our proposed MCP interface: a direct, efficient, and verifiable communication channel for our AI in Education ecosystem.
