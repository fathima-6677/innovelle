import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      region: 'ap-south-1',
      userPoolId: 'ap-south-1_n9TxDAu3z',
      userPoolClientId: '3qu3kqqt4beqo1p6r02f8l1c09',
      loginWith: {
        email: true,
      },
    } as any,
  },
});