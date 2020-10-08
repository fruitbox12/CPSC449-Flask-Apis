Project Members :
      Neeraj Polas : CWID-887414449
      Shrinidhi Pande : CWID-887347474
      Uday Reddy : CWID-894865609

How to start application?

User should have foreman installed on system to run the application. As we are having two services, we have configured them on procfile. Just run the below command in the cloned repository under flask-sqlite3 folder.

Commands:  
      cd ~/repo/flask-sqlite3
      foreman start

How to run or test the services?

We are maintaining sample input body for each and every service under Sample_Data folder. Just run the below commands to test them. If anyone want's to try custom input, edit those file and run commands mentioned below. We are using curl to call services.

CreateUser:

In order to run the create user post call from command line, run below code.

curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:5000/createUser -d @Sample_Data/createUser.json

curl -X GET -H 'Content-Type: application/json' http://127.0.0.1:5100/tweetService/v1/userTweets?userName="john_doe"

Authenticate:

Run below command to call Authenticate service from command line.

curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:5000/authenticate -d @Sample_Data/authenticate.json 


Add Follower:

Run below command to call add follower service from command line.

curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:5000/addFollower -d @Sample_Data/addFollower.json 

Remove Follower:

Run below command to call remove follower service from command line.

curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:5000/removeFollower -d @Sample_Data/removeFollower.json 