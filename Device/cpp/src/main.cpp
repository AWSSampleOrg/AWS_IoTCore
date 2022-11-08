#include <aws/crt/Api.h>
#include <aws/crt/StlAllocator.h>
#include <aws/crt/auth/Credentials.h>
#include <aws/crt/io/TlsOptions.h>
#include <aws/iot/MqttClient.h>

#include <algorithm>
#include <condition_variable>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mutex>

using namespace Aws::Crt;

int main(int argc, char *argv[])
{

    /************************ Setup the Lib ****************************/
    /*
     * Do the global initialization for the API.
     */
    ApiHandle apiHandle;

    const char *endpoint = "";
    String certificatePath = "";
    String keyPath = "";
    String caFile = "";
    String topic = "test/iot";
    String clientId = "Thing1";
    String signingRegion;
    String proxyHost;
    // uint16_t proxyPort(8080);

    String x509Endpoint;
    String x509ThingName;
    String x509RoleAlias;
    String x509CertificatePath;
    String x509KeyPath;
    String x509RootCAFile;

    // bool useWebSocket = false;
    // bool useX509 = false;

    /********************** Now Setup an Mqtt Client ******************/
    /*
     * You need an event loop group to process IO events.
     * If you only have a few connections, 1 thread is ideal
     */
    Io::EventLoopGroup eventLoopGroup(1);
    if (!eventLoopGroup)
    {
        fprintf(
            stderr, "Event Loop Group Creation failed with error %s\n", ErrorDebugString(eventLoopGroup.LastError()));
        exit(-1);
    }

    Aws::Crt::Io::DefaultHostResolver defaultHostResolver(eventLoopGroup, 1, 5);
    Io::ClientBootstrap bootstrap(eventLoopGroup, defaultHostResolver);

    if (!bootstrap)
    {
        fprintf(stderr, "ClientBootstrap failed with error %s\n", ErrorDebugString(bootstrap.LastError()));
        exit(-1);
    }

    Aws::Crt::Io::TlsContext x509TlsCtx;
    Aws::Iot::MqttClientConnectionConfigBuilder builder;

    if (!certificatePath.empty() && !keyPath.empty())
    {
        builder = Aws::Iot::MqttClientConnectionConfigBuilder(certificatePath.c_str(), keyPath.c_str());
    }

    if (!caFile.empty())
    {
        builder.WithCertificateAuthority(caFile.c_str());
    }

    builder.WithEndpoint(endpoint);

    auto clientConfig = builder.Build();

    if (!clientConfig)
    {
        fprintf(
            stderr,
            "Client Configuration initialization failed with error %s\n",
            ErrorDebugString(clientConfig.LastError()));
        exit(-1);
    }

    Aws::Iot::MqttClient mqttClient(bootstrap);
    /*
     * Since no exceptions are used, always check the bool operator
     * when an error could have occurred.
     */
    if (!mqttClient)
    {
        fprintf(stderr, "MQTT Client Creation failed with error %s\n", ErrorDebugString(mqttClient.LastError()));
        exit(-1);
    }

    /*
     * Now create a connection object. Note: This type is move only
     * and its underlying memory is managed by the client.
     */
    auto connection = mqttClient.NewConnection(clientConfig);

    if (!connection)
    {
        fprintf(stderr, "MQTT Connection Creation failed with error %s\n", ErrorDebugString(mqttClient.LastError()));
        exit(-1);
    }

    /*
     * In a real world application you probably don't want to enforce synchronous behavior
     * but this is a sample console application, so we'll just do that with a condition variable.
     */
    std::promise<bool> connectionCompletedPromise;
    std::promise<void> connectionClosedPromise;

    /*
     * This will execute when an mqtt connect has completed or failed.
     */
    auto onConnectionCompleted = [&](Mqtt::MqttConnection &, int errorCode, Mqtt::ReturnCode returnCode, bool)
    {
        if (errorCode)
        {
            fprintf(stdout, "Connection failed with error %s\n", ErrorDebugString(errorCode));
            connectionCompletedPromise.set_value(false);
        }
        else
        {
            if (returnCode != AWS_MQTT_CONNECT_ACCEPTED)
            {
                fprintf(stdout, "Connection failed with mqtt return code %d\n", (int)returnCode);
                connectionCompletedPromise.set_value(false);
            }
            else
            {
                printf("Connection completed successfully.");
                connectionCompletedPromise.set_value(true);
            }
        }
    };

    auto onInterrupted = [&](Mqtt::MqttConnection &, int error)
    {
        fprintf(stdout, "Connection interrupted with error %s\n", ErrorDebugString(error));
    };

    auto onResumed = [&](Mqtt::MqttConnection &, Mqtt::ReturnCode, bool)
    { fprintf(stdout, "Connection resumed\n"); };

    /*
     * Invoked when a disconnect message has completed.
     */
    auto onDisconnect = [&](Mqtt::MqttConnection &)
    {
        {
            fprintf(stdout, "Disconnect completed\n");
            connectionClosedPromise.set_value();
        }
    };

    connection->OnConnectionCompleted = std::move(onConnectionCompleted);
    connection->OnDisconnect = std::move(onDisconnect);
    connection->OnConnectionInterrupted = std::move(onInterrupted);
    connection->OnConnectionResumed = std::move(onResumed);

    connection->SetOnMessageHandler([](Mqtt::MqttConnection &, const String &topic, const ByteBuf &payload)
                                    {
        fprintf(stdout, "Generic Publish received on topic %s, payload:\n", topic.c_str());
        fwrite(payload.buffer, 1, payload.len, stdout);
        printf("\n"); });

    /*
     * Actually perform the connect dance.
     * This will use default ping behavior of 1 hour and 3 second timeouts.
     * If you want different behavior, those arguments go into slots 3 & 4.
     */
    printf("Connecting...\n");
    if (!connection->Connect(clientId.c_str(), false, 1000))
    {
        fprintf(stderr, "MQTT Connection failed with error %s\n", ErrorDebugString(connection->LastError()));
        exit(-1);
    }

    if (connectionCompletedPromise.get_future().get())
    {
        /*
         * This is invoked upon the receipt of a Publish on a subscribed topic.
         */
        auto onPublish = [&](Mqtt::MqttConnection &, const String &topic, const ByteBuf &byteBuf)
        {
            fprintf(stdout, "Publish received on topic %s\n", topic.c_str());
            fprintf(stdout, "\n Message:\n");
            fwrite(byteBuf.buffer, 1, byteBuf.len, stdout);
            fprintf(stdout, "\n");
        };

        /*
         * Subscribe for incoming publish messages on topic.
         */
        std::promise<void> subscribeFinishedPromise;
        auto onSubAck =
            [&](Mqtt::MqttConnection &, uint16_t packetId, const String &topic, Mqtt::QOS QoS, int errorCode)
        {
            if (errorCode)
            {
                fprintf(stderr, "Subscribe failed with error %s\n", aws_error_debug_str(errorCode));
                exit(-1);
            }
            else
            {
                if (!packetId || QoS == AWS_MQTT_QOS_FAILURE)
                {
                    fprintf(stderr, "Subscribe rejected by the broker.");
                    exit(-1);
                }
                else
                {
                    fprintf(stdout, "Subscribe on topic %s on packetId %d Succeeded\n", topic.c_str(), packetId);
                }
            }
            subscribeFinishedPromise.set_value();
        };

        connection->Subscribe(topic.c_str(), AWS_MQTT_QOS_AT_LEAST_ONCE, onPublish, onSubAck);
        subscribeFinishedPromise.get_future().wait();

        /**
         * send payload
         */
        char rp[62] = {
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};
        char tmp[100];
        srand(time(NULL));
        for (int i = 0; i < 100; i++)
        {
            tmp[i] = rp[rand() % 62];
        }
        String input = tmp;

        ByteBuf payload = ByteBufNewCopy(DefaultAllocator(), (const uint8_t *)input.data(), input.length());
        ByteBuf *payloadPtr = &payload;

        auto onPublishComplete = [payloadPtr](Mqtt::MqttConnection &, uint16_t packetId, int errorCode)
        {
            aws_byte_buf_clean_up(payloadPtr);

            if (packetId)
            {
                fprintf(stdout, "Operation on packetId %d Succeeded\n", packetId);
            }
            else
            {
                fprintf(stdout, "Operation failed with error %s\n", aws_error_debug_str(errorCode));
            }
        };
        connection->Publish(topic.c_str(), AWS_MQTT_QOS_AT_LEAST_ONCE, false, payload, onPublishComplete);

        /*
         * Unsubscribe from the topic.
         */
        std::promise<void> unsubscribeFinishedPromise;
        connection->Unsubscribe(
            topic.c_str(), [&](Mqtt::MqttConnection &, uint16_t, int)
            { unsubscribeFinishedPromise.set_value(); });
        unsubscribeFinishedPromise.get_future().wait();
    }

    /* Disconnect */
    if (connection->Disconnect())
    {
        connectionClosedPromise.get_future().wait();
    }
    return 0;
}
