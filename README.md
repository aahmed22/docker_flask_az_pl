# docker_flask_az_pl
This repo contains a simple docker flask app that will display an HTML Page via port 8000. 

**NOTE: This project code was designed to run via Azure Pipelines (Azure DevOps). The file "azure-pipelines.yml" contains the definitions of the "Build" and "Deploy" stages.**

## Part1: Examining the Dockerfile
Below is the contents of our Dockerfile:
```
FROM python:3.10

EXPOSE 8000

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt 

COPY . .

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
```

The Dockerfile definition above outlines the contents of what we'll be needing to help build our Docker Image. We start the process by adding a base image for our Docker container "python:3.10".

Following that we proceed with exposing port 8000 for our container.  

The "WORKDIR /app" sets our working directory within the container to '/app'.  

Next we copy our "requirements.txt" file which contains our packages into the /app directory. The dot (.) indicates the current working directory which in our case was set to /app. 

The 'RUN pip install' proceeds with installing the Python dependencies listed in the file inside the container.

The 'COPY . .' copies all of our content of our app from our host machine into the '/app' directory inside the container.  
***Ideally we could have avoided using the 'COPY ./requirements.txt .' since we're using this one, however I wanted to proceed with installing the packages within the container at the earlier stages of running this file.***

Finally we use 'CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]' starts the gunicorn web server when running the container based on this image. 

## Part2: Reviewing our Azure Pipeline File
Let's take a look at a portion of the Pipeline file:

```yml
trigger:
- main

resources:
- repo: self

stages:
- stage: Build
  displayName: Build image
  jobs:
  - job: StopAndDeleteContainers
    displayName: Stop and Delete Containers
    pool:
      name: ENTER_POOL_NAME
    steps:
    - script: |
        containerId=$(docker ps -qf "ancestor=ENTER_IMAGE_NAME")
        if [ -n "$containerId" ]; then
          echo "Stopping container: $containerId"
          docker stop $containerId
          echo "Deleting container: $containerId"
          docker rm $containerId
        else
          echo "No container with ancestor 'ENTER_IMAGE_NAME' found."
        fi
      displayName: Check and Stop/Delete Containers

  - job: Build
    dependsOn: StopAndDeleteContainers
    displayName: Build
    pool:
      name: ENTER_POOL_NAME
    steps:
    - script: |
        sudo docker build -t ENTER_IMAGE_NAME -f $(Build.SourcesDirectory)/Dockerfile .
      displayName: Build an image
```

**NOTE: YOU WILL NEED TO ADD YOUR OWN EXISTING POOL_NAME FROM YOUR AZURE DEVOPS ORG AND A NAME YOU WOULD LIKE FOR YOUR DOCKER IMAGE. SUBSTITUTE THE FOLLOWING "ENTER_POOL_NAME" AND "ENTER_IMAGE_NAME" WITH YOUR OWN VALUES**

The pipeline file showcases a "trigger" at the top indicating that when a change is done within the main branch then fireoff the pipeline execution. The stage we're leveraging is the "Build" stage, which consists of two jobs. The first being "StopAndDeleteContainers". When viewing the steps for this operation you will see we are attempting to see if there is a container that is running based on a specific "IMAGE_NAME". Once it locates the container that matches to the condition it will proceed to "stop" and then "remove/delete" that container. The reason I incorporated this is that I don't want to have a graveyard full of containers on the server that I am testing.  
The second job within this "Build Stage" is called "Build" which is dependent on the execution of the first job "StopAndDeleteContainers". Once the first job in that stage finishes successfully the second job "Build" will begin the proceess of building the docker image based on the Dockerfile. 

Let's proceed with the next portion of the pipeline file:

```yml
- stage: Deploy
  displayName: Deploy container
  jobs:
  - job: RunContainer
    displayName: Run Container
    pool:
      name: ENTER_POOL_NAME
    steps:
    - script: |
        sudo docker run -d -p 8000:8000 ENTER_IMAGE_NAME
      displayName: Run Docker container
```

This section of the file showcases the "Deploy" Stage, which has a single job operation called "RunContainer". Once the two jobs finishes running during the Build stage it will proceed with excuting this stage and run the container based on the newly constructed Docker Image we just built. There you have it this command `sudo docker run -d -p 8000:8000 ENTER_IMAGE_NAME` will proceed with running your container. 

**NOTE: PLEASE BE ADVISED YOU WILL HAVE TO ALREADY HAVE YOUR MACHINE NETWORK SECURITY GROUPS CONFIGURE TO ALLOW TRAFFIC TO PORT 8000. MY RECOMMENDATION IS TO HAVE PORT 8000 OPEN TO JUST YOUR IP ADDRESS SINCE WE ARE ONLY DOING TESTING.**

## Part3: HTML PAGE
So here is a preview of what the Docker Flask App should render when you access your "SERVER_IP_ADDRESS:8000" via browser:

![HTML OUTPUT](/snapshots/html_output.PNG)

Here is the HTML code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Testing</title>
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='main.css') }}">
</head>
<body>
    <h1>Lorem Ipsum</h1>
 

    <p>
        Let's begin testing...
    </p>

    <blockquote>
        Lorem ipsum dolor sit amet consectetur adipisicing elit. Doloribus minus, molestias officia unde qui corrupti magnam eum suscipit quis eligendi reiciendis, alias, sapiente veritatis illo placeat fuga quasi temporibus doloremque.
        Lorem ipsum dolor, sit amet consectetur adipisicing elit. Sed provident mollitia fuga necessitatibus, ad nostrum quidem voluptatum architecto sunt harum molestiae dolore, vel eum eos doloremque quae omnis aliquam quasi.
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ratione nobis, hic autem doloribus, alias suscipit esse laborum nulla beatae, repellat vero accusantium praesentium inventore error molestias? Ea eius nihil fugiat.
    </blockquote>

    <a href="#">Check out my GitHub account! <span class="finger">👉</span></a>
</body>
</html>
```

I would recommend placing your GITHUB URL within the "anchor element" : `<a href="ENTER_GITHUB_URL">`  
Or any other URL you want for testing out the page.

Best of luck!