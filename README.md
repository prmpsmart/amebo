# Amebo

### Chat Room Type

1. Direct Message
2. Group
3. Channel

> We'll be using WebSockets for the connection.
>
> We'll have to decide whether we should use phone numbers like WhatsApp or email or username/id or link it all up so that none of them is used by multiple people in our verification

### Models
1. User
    - properties
        - name
        - description/bio
        - username/id
        - date_created
        - contacts
        - groups
        - channels
2. Chat
    - type
        - text
        - image
        - audio/voice [later]
        - video [later]
        - link
    - properties
        - content
        - text [some images or voice or video may have text written below them]
        - author
        - recipient
        - chat_room_type

### Connection subclasses of websockets
1. Client
2. Server 
