# IS601-FinalWebApp-TeamProject

## Group Member Names
#### Stanley Ordonez
#### Michael Drozdowski

## Project Concept
* The overall concept of this project is to view cities from around the world. The user will be able to view cities from countries across the globe, edit the data for those cities, add new cities to the list, and delete an entry.
* **The additional features that we have added are:**
    * A login and registration system where users can create new accounts for the website. This feature uses email verification, and user who do not verify their email will not be allowed to login.
    * A profile page where users can view their profile information such as their username and email, change their profile information, and change their password.
  
## Added Features
* **Log-In & Registration with E-mail Verification (Michael)**
  * Users can register an account with our website.
  * After registering users must verify their email.
  * After verification users can log in and log out of our website using the username and password that they made.
* **Profile Page and Changing User Data (Stanley)**
  * Users can view their profile information.
  * Users can edit and change their profile information.
  * Users can change their passwords.
  
## Installation Instructions
1. Clone this Github repository to your local machine (Note: You must have Docker Desktop installed)
2. Download the ".env" file from the canvas submission and place it in the directory/folder where the cloned project is stored
3. Run the program by having a docker-compose configuration on Pycharm or by running a "docker-compose up" command on the "main" branch
4. Go to localhost:5000 or 0.0.0.0:5000 to view the web application
5. Register a new account with a username, password, and a **valid** email that you have access to
6. Once you click register and you will receive the confirmation code in an email from "mikeandstanley.website@gmail.com"
7. Copy and paste the confirmation code into the box on the confirmation page
8. Once confirmed, you can login into the account that you just registered 
9. Enjoy!

## Developer Notes
Our gmail account information as well as admin account information is inside of the .env file. You can log into the admin account by using the credentials inside of the .env file.