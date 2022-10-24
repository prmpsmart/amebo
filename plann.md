# **Structure for AmeboChat**

More features will be added by the *community (you)* as we progress.

## **Models**
- **Object**

    `properties`: **id**, **created_at**.

    `subclasses`:
    
    - **Profile**
        
        `properties`: **display_name**, **description**, **avatar** (image) plus **Objects** properties too.
        
        `subclasses`:
        
        - **MemberRole**
        
            `properties`: **permissions**.
        
        - **User**
            
            `properties`: **unique_id**, **password**, **last_seen**, **status**. **direct_messages**, **contacts**, **groups**, **broadcast_channels**. `unique_id` can be anything like username, email, phone number, NIN, matric number etc.
            
            `subclasses`: 
            
            - **Bot**
                
                `properties`: **api_key**
        
        - **Room**
            
            `properties`: **messages**, **members**, **pinned_message**.
            
            `subclasses`:
            
            - **SubRoom**
                
                `properties`: **roles**.
            
            - **Group**
                `properties`; **creator**, **roles**, **sub_rooms**.
                
                `subclasses`:
                
                - **Broadcast**
                    It's a type of **Group** but the **SEND_MESSAGE** permission is restricted and not available for everyone.
  - **Message**
      
      `properties`: **author**, **type**, **text**, **attachment**, **attachment_type**, **reply_message_id**, **status**, **forwarded**, **forwarder**, **forwarded_at**, **forwarded_from**, **members_delivered_to**, **members_read**.
      
      `subclasses`:
      - **DirectMessage**
          
          `properties`: **recipient**.
      - **RoomMessage**
          
          `properties`: **room**, **room_type**.
          - **SubRoomMessage**
              
              `properties`: **main_room**.
- **MemberPermissions**

    `properties`: **MANAGE_ROOM**, **MANAGE_ROLES**, **MANAGE_MESSAGES**, **MANAGE_MEMBERS**, **MANAGE_SUBGROUPS**, **MANAGE_INVITES**, **SEND_MESSAGES**, **EMBED_LINKS**, **ATTACH_FILES**.

- **Member**
    
    `properties`: **joined_at**, **user**, **roles**, **inviter_id**, **room**, **room_type**.

- **MessageType**
    
    `properties`: **TEXT**, **AUDIO**, **IMAGE**, **VIDEO**.

- **RoomType**
    
    `properties`: **GROUP**, **SUB_GROUP**, **BROADCAST_CHANNEL**.

## **Messaging Channels**
- **DIRECT_MESSAGE**
    The one on one type of messaging.
- **GROUPS**
    A room where many people chat simultaneously.
    - **SUB_GROUPS**
        A smaller room created by privileged person's in the room for special purpose.
        e g a sub group for admins in the room (no need to create another group for
        admins) Like we have on AmeboChat, AmeboUI, AmeboServer groups differently,
        AmeboChat will just be the mother group and the other teams group will be
        sub groups just like in discord. ![discord](discord.jpg)
- **BROADCAST_CHANNEL**
    Exactly like **GROUPS** but the **EVERYONE** Permission is revoked, so not everyone 
    can contribute in the channel, they just react to the messages.

## **PERMISSIONS**
- **MANAGE_ROOM**
    Manage room details and everyother thing in the room, the highest permission. Manage everyother permissions in this room.
- **MANAGE_ROLES**
    Manage the roles in the room, add or delete roles, add or remove members to or from a role. also manage the permissions of each roles.
- **MANAGE_MESSAGES**
    Manage messages in the room, delete messages or pin message.
- **MANAGE_MEMBERS**
    Manage members in the room, add or delete members to or from the room.
- **MANAGE_SUBGROUPS**
    Manage subgroups, add or delete subgroups, change avatar, name and description of subgroups
- **MANAGE_INVITES**
    Have access to the room invite link, and can add members to the room, but can't delete them from the room.
- **SEND_MESSAGES**
    Able to send messages in the room
- **EMBED_LINKS**
    Make links send into the room clickable, when a member without this permission send a message that has a link in it, the link won't be clickable from the app.
- **ATTACH_FILES**
    Able to send files into the room (images, audio, pdf, doc etc).

## ACTIONS
- **SIGN**
    - **SIGN_IN**
    - **SIGN_UP**
    - **SIGN_OUT**

- **SUB_GROUP**
    - **CREATE_SUB_GROUP**
    - **DELETE_SUB_GROUP**
    - **SET_MEMBER_ROLE**
        Role that can be in this group. People with this role in the main group will be able to interact in this subgroup.
    - **SET_VISIBILITY**
        Whether to hide this subgroup from people without the assigned role.

- **GROUP** 
    **`BROADCAST`** also has its own by replacing `GROUP` with `BROADCAST` in the following actions.
    - **CREATE_GROUP**
    - **ADD_MEMBER**
    - **REMOVE_MEMBER**
    - **BAN_MEMBER**
    - **ADD_ROLE**
    - **REMOVE_ROLE**
    - **SET_MEMBER_ROLE**
    - **REMOVE_MEMBER_ROLE**
    - **EDIT_GROUP_INFO**
    - **EDIT_GROUP_AVATAR**
    - **EDIT_GROUP_NAME**
    - **EDIT_GROUP_DESCRIPTION**
    - **CREATE_GROUP_INVITE_LINK**
    - **REVOKE_GROUP_INVITE_LINK**
    - **JOIN_GROUP**
    - **LEAVE_GROUP**
    - **DELETE_GROUP**
    - **SET_PINNED_MESSAGE**
    - **SEND_MESSAGE_TO_GROUP**
    
- **MESSAGE**
    - **DELETE_MESSAGE**
    - **CLEAR_MESSAGES**
    - **FORWARD_MESSAGE**
    - **EDIT_MESSAGE**
    - **REPLY_TO_MESSAGE**
    - **MESSAGE_STATE**
        Whether message is sent, delivered, or read.
 
- **USER**
    - **CREATE_USER**
    - **EDIT_USER_INFO**
    - **EDIT_USER_NAME**
    - **EDIT_USER_AVATAR**
    - **EDIT_USER_DESCRIPTION**
    - **DELETE_USER**
