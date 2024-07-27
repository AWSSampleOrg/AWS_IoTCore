import type { PostConfirmationTriggerHandler } from "aws-lambda";
import {
  IoTClient,
  CreateThingCommand,
  AttachPolicyCommand,
} from "@aws-sdk/client-iot"; // ES Modules import

export const handler: PostConfirmationTriggerHandler = async (event) => {
  console.log(JSON.stringify(event));

  const client = new IoTClient({ region: process.env.AWS_REGION });

  await client.send(
    new CreateThingCommand({
      thingName: `${event.userName}-thing`,
    })
  );

  return event;
};
