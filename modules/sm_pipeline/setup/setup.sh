#
# Step 1: SSH into your ec2 instance
# Step 2: Execute the following command

# Create local directory mapping
sudo mkdir -p /opt/ml
sudo mkdir -p /opt/ml/processing/model/
sudo chown -R ec2-user:ec2-user /opt/ml
