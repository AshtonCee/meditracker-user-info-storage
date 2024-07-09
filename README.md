# meditracker-user-info-storage

Used to store and authenticate user info

## Description

Sends inputted user info, such as username, email, and password, from MediTracker.com and then sends that data to a DynamoDB database. This was turned into an API in order to allow interactivity between MediTracker frontend and this Python backend.

## Getting Started

### Roadmap

* More functions to allow for more specific API method calling
  ** Individual password replacement without fully updating entire DB item
* Integrate into MediTracker.com
* Authenticate users to see if information is already stored in the database.
