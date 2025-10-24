# Interactive Installation Setup

## Prerequisites
- Ensure an OTOBO or Znuny system is available. The installer automatically detects whether the host is running an OTOBO Docker installation, a standalone OTOBO installation, or a Znuny installation.
- Have administrator credentials ready so that new users, groups, queues, and web services can be created.

## Installation Detection
1. Start the setup tool. It determines the underlying platform (OTOBO Docker, OTOBO, or Znuny).
2. Confirm the detected installation type before continuing.

## User Creation
1. Decide whether to create a new user for OpenTicketAI access.
2. If creating a user, review or adjust the default values:
   - **Login**: `open_ticket_ai`
   - **First name**: `Open Ticket`
   - **Last name**: `AI`
   - **Email**: `open_ticket_ai@localhost`
   - **Password**: automatically generated
3. Specify the queue that should receive incoming tickets. The default queue is **Incoming Tickets**.
4. If the queue's group does not exist, create it. The default group is **users**.
5. Grant the new user the following permissions for the selected queue: Owner, Note, Move, Priority, and Lock.
6. When prompted, decide whether the user should receive full permissions. If yes, grant full system-wide permissions.
7. Note any additional permissions that administrators may need to configure manually after the setup completes.

## Web Service Setup
1. Choose whether to create a new web service. The default name is **OpenTicketAI**.
2. Decide if the web service should be restricted to the newly created user.
3. Select the operations that the service will expose. Available options include:
   - `TicketCreate`
   - `TicketUpdate`
   - `TicketSearch`
   - `TicketGet`
4. Generate the web service configuration.
5. Depending on the detected installation type, move the configuration file to the appropriate location and adjust file permissions accordingly.
6. Run the OTOBO command that imports or registers the web service configuration.

## Verification and Testing
1. Choose whether to test the web service immediately.
2. If the `TicketCreate` operation is enabled:
   - Send a test request to create a ticket in the configured queue.
   - Confirm that the ticket appears in the queue.
3. If `TicketCreate` is not enabled:
   - Manually create a ticket in the Incoming Tickets queue.
   - Confirm that the ticket is available for further operations.
4. Run automated tests:
   - Search the queue for the test ticket.
   - Retrieve the ticket by ID using `TicketGet`.
   - Update the ticket with a note via `TicketUpdate`.

## Final Steps
1. Store the generated `OTOBO_PASSWORD` in an environment variable for later use.
2. Create a `config.yaml` file that captures the key configuration values determined during setup.
