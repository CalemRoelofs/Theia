# Theia - Web Application Server Sentinel  

For my end of year project for my course in contemporary software development, I've decided to create a server monitor combining elements of Nagios, OpenVAS and MxToolbox.  
Theia is going to fulfil a number of roles:
- Registry of applications  
    - Keep track of what apps live on what servers
    - Who wrote them
    - Who maintains them
    - When they were deployed
- Passive security auditing
    - What ports are open?
    - Are the SSL certs valid?
    - Are the proper security headers in place?
    - What's the latency to the host?
- State change alerting
    - Some ports just opened on a server?
    - The SSL certs just expired?
    - Someone just changed the `content-security-policy`?
    - Notify the sysadmins/devops/developer to let them know via:
        - Slack
        - Discord
        - Telegram
        - Microsoft Teams
        - Email with SMTP

The basic idea is to have an application in place that not only tracks what infrastructure is in place, but also maintains historic records of certain changes that happen to that infrastructure for auditing at a later date, or alerting administrators immediately of something unexpected.

## Usage
```bash
docker-compose up -d --build
```  

The server will run on port 8080 by default but this can be changed in the `docker-compose.yml` file.  
If you want to use the Django Admin Panel, to set up a superuser find the id of the container and run `docker exec -it {container_id} python manage.py createsuperuser`.  
  
## To-Do  
- Test CRUD validations for:  
    - Servers  
    - Webhooks  

- Implement:  
    - Exporting changelog history for a server   
  
- Bugs:  
    - Messages aren't rendering in Teams for some reason despite being returned 200  
  
- Nice to have:  
    - Format messages properly    
    - Add a basic login system   
    - Allow users to see the profile history for a server at a given date/time  
    - Figure out what else to put in the top navbar   
    - Add pagination for changelogs and alertlogs    
    - Write a nicer and more descriptive README  
