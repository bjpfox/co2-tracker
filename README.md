# co2-tracker
For project 2 of the General Assembly Software Engineering Immersive, I plan to build a carbon emissions tracker app which allows users to track the carbon emissions associated with their use of transport and household energy.


### Structure of web app
The app will comprise the following pages / features:
* User sign up page
* Ability to add new emissions 'events' 
* Ability to edit / delete previously entered data 
* Ability to use pre-loaded emissions data, or to manually enter own emissions rates
* Ability to view a simple dashboard summary of results 


### Extensions 
If time I may add some of the following:
* Ability to export data as csv file
* Ability to share results with friends/family
* Comparison / benchmarking against others
* Interface with an external API - if it makes sense, e.g. carbon offsets
* Store images using AWS S3
* Add some JS, e.g. form validation
* Ability to import data from csv
* Mobile friendly
* Provide as an external API


### Challenges
* How to do the visualisation, such as a pie chart or line graph? Explore using Google Chart tools (uses JS)

### Things to think about 
* Can OOP be used here? What objects would make sense?
    * Emissions event
        * Methods: ?  
    * User 
        * Methods: create_new_event(), edit_event(), delete_event()? 


### Design decisions to make
*

### User stories 
As a user, I want to:
* Quickly enter data, even if I don't know the specific emissions rate 
* Get some insights into my carbon emissions 


### Technology used
* Web server: Python flask
* Database: postgresql 
* Front end: HTML, CSS, Javascript, Google Charts


### Technical aspects
* TBC


### References
1. Google Charts documentation: https://developers.google.com/chart