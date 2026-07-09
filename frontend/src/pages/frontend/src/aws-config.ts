import { Amplify } from "aws-amplify";

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: "ap-south-1_n9TxDAu3z",
      userPoolClientId: "3qu3kqqt4beqo1p6r02f8l1c09",
    },
  },
});