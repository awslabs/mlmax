FROM node:latest
RUN cd /root && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install && rm -rf awscliv2.zip
RUN npm install -g @aws-amplify/cli
RUN npm install -g aws-amplify @aws-amplify/ui-react
RUN npm install -g uuid
CMD tail -f /dev/null
