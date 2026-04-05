import * as iot from "aws-cdk-lib/aws-iot";
import { Construct } from "constructs";

export class IoT extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    new iot.CfnPolicy(this, "IoTPolicy", {
      policyName: "iot-policy-for-cognito-auth",
      policyDocument: {
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Action: [
              "iot:Connect",
              "iot:Publish",
              "iot:Subscribe",
              "iot:Receive",
            ],
            Resource: ["*"],
          },
        ],
      },
    });
  }
}
