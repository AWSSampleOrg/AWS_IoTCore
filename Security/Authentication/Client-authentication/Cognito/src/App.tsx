import {
  confirmSignUp,
  ConfirmSignUpInput,
  fetchAuthSession,
  signIn,
  SignInInput,
  signUp,
  SignUpInput,
} from "aws-amplify/auth";
import { PubSub } from "@aws-amplify/pubsub";
import { Authenticator } from "@aws-amplify/ui-react";
import { AttachPolicyCommand, IoTClient } from "@aws-sdk/client-iot";
import "@aws-amplify/ui-react/styles.css";
import { useState } from "react";
import { CONNECTION_STATE_CHANGE, ConnectionState } from "@aws-amplify/pubsub";
import { Hub } from "aws-amplify/utils";

const PUBSUB = new PubSub({
  region: import.meta.env.VITE_AWS_REGION,
  endpoint: import.meta.env.VITE_IOT_ATS_ENDPOINT,
});

const services: Parameters<typeof Authenticator>[0]["services"] = {
  async handleSignIn(input: SignInInput) {
    return signIn({
      ...input,
      options: {
        authFlowType: "USER_SRP_AUTH",
      },
    });
  },
  async handleSignUp(input: SignUpInput) {
    return signUp(input);
  },
  async handleConfirmSignUp(input: ConfirmSignUpInput) {
    return confirmSignUp(input);
  },
};

function App() {
  const [messages, setMessage] = useState<string[]>([]);
  const [status, setState] = useState<string[]>([]);
  const [count, setCount] = useState(0);
  const [sub, setSub] = useState<any>();
  const defaultTopic = "test/iot";

  const handlePublish = async () => {
    setCount((c) => c + 1);
    await PUBSUB.publish({
      topics: defaultTopic,
      message: { index: count },
    });
    console.log("Published!");
  };

  const handleSubscribe = async () => {
    const session = await fetchAuthSession();

    const client = new IoTClient({
      region: import.meta.env.VITE_AWS_REGION,
      credentials: session.credentials,
    });
    await client.send(
      new AttachPolicyCommand({
        policyName: "iot-policy-for-cognito-auth",
        target: session.identityId,
      })
    );

    const sub = PUBSUB.subscribe({
      topics: defaultTopic,
    }).subscribe({
      next: (data) => {
        console.log("Message received", data);
        setMessage((messages) => [...messages, JSON.stringify(data)]);
      },
      error: console.error,
      complete: () => {
        console.log("Done");
      },
    });
    setSub(sub);
    console.log("subscribed!");
  };

  const handleUnsubscribe = async () => {
    await sub.unsubscribe();
    console.log("Unsubscribed!");
  };

  const handleHub = async () => {
    Hub.listen("pubsub", (data) => {
      const { payload } = data;
      if (payload.event === CONNECTION_STATE_CHANGE) {
        setState((status) => [
          ...status,
          (data.payload.data as { connectionState: ConnectionState })
            .connectionState,
        ]);
      }
    });
    console.log("Hub listened!");
  };

  return (
    <Authenticator services={services}>
      {({ signOut, user }) => (
        <main>
          <h1>Hello {user?.username}</h1>
          <button onClick={signOut}>Sign out</button>
          <hr />
          <button onClick={() => handlePublish()}>publish</button>
          <button onClick={() => handleSubscribe()}>subscribe</button>
          <button onClick={() => handleUnsubscribe()}>unsubscribe</button>
          <ul>
            {messages.map((message, index) => {
              return <li key={index}>{message}</li>;
            })}
          </ul>
          <hr />
          <button onClick={() => handleHub()}>hub listen</button>
          <ul>
            {status.map((state, index) => {
              return <li key={index}>{state}</li>;
            })}
          </ul>
          <hr />
        </main>
      )}
    </Authenticator>
  );
}

export default App;
