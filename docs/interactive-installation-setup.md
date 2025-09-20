First Start Setup

Automatically detect if there is an otobo docker installation a otobo installation or a znuny installation.

Then ask if a new user should be created
provide default names
login: open_ticket_ai
firstname: Opem Ticket
lastname: AI
email: open_ticket_ai@localhost
password: (randomly generated)

Ask for the incoming tickets queue
default Incoming Tickets

Then check what group the queue belongs to
if doesnt exist: create group: default group: users

Give the User permissions to Owner, Note, Move, Priority and Lock tickets in this queue

Tell the User to update permissions of the newly created User if they also need additional permissions.
Aks if User should just get full permissions:
If Yes: give full permissions

Then ask to create webservice:
default name: OpenTicketAI

Aks if webservice should be restricted to that user.

Then ask what operations should be allowed:
TicketCreate
TicketUpdate
TicketSearch
TicketGet

Then create the Webservice config.

Depending on the installation type, move Webservice to correct location and set correct permissions.

Execute OTOBO Command to Add Webservice.

Aks if the Webservice setup should be tested now.
If TicketCreate Operation allowed this is easy to test.
Otherwise tell the User to create a Ticket in the Incoming Queue now!
Then confirm if ticket is created.

Now run the tests, search for ticket in Incoming Queue.
Get Ticket by Id and then Update the Ticket with a note.

Save the OTOBO_PASSWORD in an env var.

And create a config.yaml filw with the important configs that have been set.