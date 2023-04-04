# co2-tracker
For project 2 of the General Assembly Software Engineering Immersive, I plan to build a carbon emissions tracker app which allows users to track the carbon emissions associated with their use of transport and household energy.


### Structure of web app
The app will comprise the following pages / features:
* User sign up page 
* Ability to add new emissions 'events' 
* Ability to edit / delete previously entered data 
* Ability to use pre-loaded emission rates, or to manually enter own emissions rates 
* Ability to view a simple dashboard summary of results 

### Screenshots
![Screenshot of the co2 tracker dashboard]('./static/img/co2-tracker-dashboard.png')


### User stories 
As a user, I want to:
* Quickly enter data, even if I don't know the specific emissions rate 
* Enter custom emissions (kg co2), if I have an event that the app doesn't have an emission rate for 
* Get some insights into my carbon emissions 


### Technology used
* Web server: Python flask
* Database: postgresql 
* Front end: HTML, CSS, Javascript, Google Charts


### Technical aspects
* Object oriented programming approach - used Emission class with methods get_units() and get_date(), User class for app users
* Architectural pattern: Model View Controller


### Challenges
* Calculating daily emissions using emission events with different units (MJ, kWh, km, etc) and different time periods (daily, monthly, quarterly) and start dates
* Getting robust data for all emission types (e.g. train) 
* Google Charts - limited options for controlling display of chart, some gaps in documentation
* Maintaining consistent layout for different data volumes (as charts get bigger / smaller, etc)

### Future work
* Add electricity rate data for different states and territories 
* More research into emission rates
* Provide ways to export data e.g. csv 
* Make dashboard more interactive, e.g. collapsable / movable graphs
* Explore ways to link to APIs, e.g. for purchasing climate credits, or climate news 
* Develop an FAQ


### References
1. Google Charts documentation: https://developers.google.com/chart
2. Google Charts documentation (detailed guide): https://developers.google.com/chart/interactive/docs/gallery/areachart#Configuration_Options 