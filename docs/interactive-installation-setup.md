# Interactive Installation and Setup

This guide describes the interactive workflow for preparing OTOBO, Znuny, or OTOBO Docker environments for use with
`otobo_znuny_python_client`. Each step outlines the prompts the helper script should show and the actions it performs
behind the scenes.

## Prerequisites

1. Detect the type of installation (OTOBO Docker, on-premises OTOBO, or Znuny) before presenting any prompts.
2. Confirm that the operator has administrative permissions to create users, groups, and web services.
3. Generate a secure random password that can be shown to the operator after the account is created.

## Create a Dedicated API User

1. Ask whether a dedicated API user should be created. If the operator declines, skip to the web service configuration.
2. Provide these defaults, allowing the operator to override each value:
   - **Login:** `open_ticket_ai`
   - **First name:** `Open Ticket`
   - **Last name:** `AI`
   - **Email:** `open_ticket_ai@localhost`
   - **Password:** random value generated in the prerequisites step
3. Ask for the incoming queue that should receive tickets. Default to **Incoming Tickets**.
4. Determine which group owns the queue. If no group exists, create one (default name: **users**).
5. Grant the new user the following permissions on the queue: Owner, Note, Move, Priority, and Lock.
6. Offer to grant full system permissions if the operator indicates the account should not be restricted to the queue.
7. Remind the operator to adjust the user's permissions later if they require additional access.

## Configure the Web Service

1. Ask whether the helper should create a web service now. Use **OpenTicketAI** as the default name.
2. Prompt whether the web service should be restricted to the API user created earlier.
3. Offer the following operations for inclusion in the web service configuration:
   - `TicketCreate`
   - `TicketUpdate`
   - `TicketSearch`
   - `TicketGet`
4. Generate the web service configuration based on the selected operations and permissions.
5. Place the resulting configuration file in the correct directory for the detected installation type and update file
   permissions accordingly.
6. Execute the appropriate OTOBO console command to register or update the web service.

## Verify the Setup

1. Ask the operator if the web service should be tested immediately.
2. If `TicketCreate` is enabled, send a test ticket to the selected queue. Otherwise, instruct the operator to create a
   test ticket manually.
3. Confirm that the ticket exists, retrieve it by ID, and add a note to verify update permissions.
4. Surface any failures so the operator can adjust the configuration before continuing.

## Store Credentials and Configuration

1. Prompt the operator to save the generated password in an environment variable named `OTOBO_PASSWORD`.
2. Write a `config.yaml` file that captures the final base URL, web service name, allowed operations, and the login
   details for the API user.
3. Display a summary of the configuration so the operator can verify the stored values.
