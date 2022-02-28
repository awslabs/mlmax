source config/cicd.ini

deploy () {
    aws cloudformation deploy \
      --region=${Region} \
      --stack-name ${StackName} \
      --template-file ./cicd.yaml \
      --parameter-overrides $(cat config/cicd.ini) \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM CAPABILITY_AUTO_EXPAND
}

deploy
