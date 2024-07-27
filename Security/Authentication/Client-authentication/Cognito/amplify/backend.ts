import { defineBackend } from "@aws-amplify/backend";
import { auth } from "./auth/resource";
import { postConfirmation } from "./functions/post-confirmation/resource";
import { UserPool, UserPoolOperation } from "aws-cdk-lib/aws-cognito";
import * as iam from "aws-cdk-lib/aws-iam";
import { IoT } from "./custom/iot/resource";

/**
 * @see https://docs.amplify.aws/react/build-a-backend/ to add storage, functions, and more
 */
const backend = defineBackend({
  auth,
  postConfirmation,
});

backend.postConfirmation.resources.lambda.addToRolePolicy(
  new iam.PolicyStatement({
    effect: iam.Effect.ALLOW,
    actions: ["iot:*", "iotjobsdata:*"],
    resources: ["*"],
  })
);

backend.auth.resources.authenticatedUserIamRole.addManagedPolicy(
  iam.ManagedPolicy.fromAwsManagedPolicyName("AWSIoTFullAccess")
);
(backend.auth.resources.userPool as UserPool).addTrigger(
  UserPoolOperation.POST_CONFIRMATION,
  backend.postConfirmation.resources.lambda
);

new IoT(backend.createStack("IoTPolicy"), "IoTPolicy");

backend.addOutput({
  custom: {
    func: backend.postConfirmation.resources.lambda.functionName,
  },
});
