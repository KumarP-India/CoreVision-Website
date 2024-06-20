# Backend servers

This guide will walk you through setting up backend server solution. The form submissions are first sent to a Raspberry Pi. If the Raspberry Pi is unavailable, the submissions will be sent to AWS as a backup.

## Prerequisites

- Raspberry Pi with Raspbian installed
- AWS Account
- Basic knowledge of Python and AWS services

## Raspberry Pi Setup

### Step 1: Install Python and Flask

1. Update your Raspberry Pi:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. Install Python and Flask:
   ```bash
   sudo apt install python3 python3-pip
   pip3 install flask
   ```

### Step 2: Get the Server files

1. The files are in Repository and thus clone it:
    ```bash
    git clone https://github.com/KumarP-India/CoreVision-Website.git
    ```

2. Next we need to get onlt the files that are required in Pi. They are in folder `<Repo>/Backend Server/Raspberry Pi`:
    ```bash
    cd Desktop
    cp 'CoreVision-Website/Backend Server/Raspberry Pi' ./bin
    ```

    We can even remove all other files, or in this case remove the cloned copy.

    ```bash
    rm -R 'CoreVision-Website'
    ```

### Step 3: Setup the Pi OS

1. Setup Autostart

    Create a systemd service file to run the Flask app on boot:

    ```bash
    sudo nano /etc/systemd/system/form_submission.service
    ```

    Add following in the text editor then save it by by `Ctrl + X` then `Y`:

    ```ini
    [Unit]
    Description=Form Submission Flask App
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /home/pi/Desktop/bin/app.py
    WorkingDirectory=/home/pi/Desktop
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=KumarP-India

    [Install]
    WantedBy=multi-user.target
    ```

2. Refresh the systemd manager configuration by reloading and enable our service to start on boot

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable form_submission.service
    ```

3. Start our service

    ```bash
    sudo systemctl start form_submission.service
    ```

### Step 4: Configure Router for Port Forwarding

To make your Raspberry Pi accessible from the internet, you need to set up port forwarding on your router.

1. Get Mac and IP of Raspberry pi:
    - In raspberry Pi terminal run `ip addr show`
    - Look under section `eth<number>`
    - Note down IP that look like `192.168.<number>.<number>`
    - Note down MAC address that has 6 pair of 2 charector or 2 digit or 1 charector & 1 digit seperated by `:`. FOr example `b8:27:eb:45:67:89`
2. Log in to your router's web interface (usually accessible via `192.168.1.1` or similar).
3. Find the port forwarding section (this might be under "Advanced", "NAT", or "Firewall").
4. Add a new port forwarding rule:
   - **Service Name**: CoreVision
   - **External Port**: 5000
   - **Internal IP**: [Your Raspberry Pi's local IP address; We saved this in `1`] (e.g., 192.168.1.100)
   - **Internal Port**: 5000
   - **Protocol**: TCP
4. Now we need to asign Static IP to our server. 
    - Find the Static Asignment (Usully under sections like "LAN Setup", "Advanced Settings", or "DHCP".)
    - Find the section for DHCP reservations or static leases.
    - Enter the MAC address of your Raspberry Pi. [The one you saved in `1`]
    - Enter the IP address of your Raspberry Pi. [The one you saved in `1`]
    - Save it and enable it

5. Save the settings and reboot your router if necessary.

### AWS Setup

#### Step 1: Create an S3 Bucket

1. Go to the [S3 Console](https://console.aws.amazon.com/s3/home) and create a new bucket.
2. Name the bucket (e.g., `corevision-website-form-backup-data`) and configure it according to your needs.

#### Step 2: Create an AWS Lambda Function

1. Go to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/home) and create a new function.
2. Choose the `Author from scratch` option.
3. Set up the function with the following details:
   - Name: `CoreVisionWebsiteFormSubmissionHandler`
   - Runtime: `Python 3.x`
   - Role: Choose an existing role > `CoreVisionWebsiteFormRole`

#### Step 3: Add Lambda Function Code

1. Add the following code to the Lambda function:

   ```python
   import json
   import boto3

   def lambda_handler(event, context):
       s3 = boto3.client('s3')
       bucket_name = 'corevision-website-form-backup-data'
       file_name = 'CoreVision-Website-Form-data.json'

       data = json.loads(event['body'])

       try:
           current_data = s3.get_object(Bucket=bucket_name, Key=file_name)
           current_data = json.loads(current_data['Body'].read())
       except s3.exceptions.NoSuchKey:
           current_data = []

       current_data.append(data)

       s3.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(current_data))

       return {
           'statusCode': 200,
           'body': json.dumps({'status': 'success'})
       }
   ```

2. Deploy the Lambda function.

#### Step 4: Create an API Gateway

1. Go to the [API Gateway Console](https://console.aws.amazon.com/apigateway/home) and create a new REST API.
2. Create a new resource and add a POST method.
3. Set the integration type to Lambda Function and choose the `FormSubmissionHandler` function.
4. Deploy the API and note the endpoint URL.

### Final Steps

1. Test the form submission to ensure it first tries to send data to the Raspberry Pi.
2. If the Raspberry Pi is unavailable, the form submission should fallback to AWS and store the data in the S3 bucket.

With this setup, your form data will be saved locally on the Raspberry Pi if it's online and available. If the Raspberry Pi is offline, the data will be sent to AWS and stored in an S3 bucket, ensuring no data loss and cost efficiency.