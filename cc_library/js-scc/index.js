const Paho = require("paho-mqtt");

class Message {
  constructor(device_id, type, contents) {
    this.device_id = device_id;
    this.time_sent = formatDate(new Date());
    this.type = type;
    this.contents = contents;
  }
}

class SccLib {
  constructor(config, device, logger) {
    this.device = device;
    this.name = config.id;
    this.info = config.description;
    this.host = config.host;
    this.port = config.port;
    this.labels = config.labels;
    this.log = function(level, message) {
      logger(new Date(), level, message);
    };
    this.log("info", "Start of log for device: " + this.name);

    // setup mqtt
    this.client = new Paho.Client(this.host, this.port, "", this.name);
    this.client.onMessageArrived = msg => {
      this._onMessage(msg);
    };

    /**
     * _onConnect gets called when trying to connect,
     * it subscribes to all specified topics
     * it sends a connection true message
     * it logs that it connected
     * @private
     */
    this._onConnect = function() {
      for (let label in this.labels) {
        this.client.subscribe(label);
      }
      this.client.subscribe("client-computers");
      this.client.subscribe(this.name);

      this._sendMessage(
        "back-end",
        new Message(this.name, "connection", {
          connection: true
        })
      );
      this.log("info", "connected OK");
    };

    /**
     * _onConnectFailure is a method that gets called when connecting failed
     * it will log an error and try to reconnect on a regular interval till it succeeds
     * @private
     */
    this._onConnectFailure = function() {
      let retryCooldown = 10 * 1000; // 10 seconds before retrying to connect
      this.log(
        "error",
        "connecting failed, retry in " + retryCooldown + " seconds"
      );
      setTimeout(() => {
        this.connect();
      }, retryCooldown);
    };

    this._onMessage = function(message) {
      this.log(
        "info",
        "message received:\n topic: " +
          message.topic +
          ",\n message: " +
          ",\n message: " +
          message.payloadString
      );
    };
  }

  /**
   * _sendMessage sends an mqtt message to SCILER
   * @param topic string containing the mqtt topic
   * @param message json that should follow the message_manual.md
   * @private
   */
  _sendMessage(topic, message) {
    let msg = new Paho.Message(JSON.stringify(message));
    msg.destinationName = topic;
    this.client.send(msg);
  }

  /**
   * connect connects to SCILER
   * sets up a LWT (Last Will and Testament)
   * sets up handlers for connection and connection failure
   * sets up automatic reconnect
   */
  connect() {
    let will = new Paho.Message(
      JSON.stringify({
        topic: "back-end",
        payloadString: JSON.stringify(
          new Message(this.name, "connection", {
            connection: false
          })
        )
      })
    );
    will.destinationName = "back-end";
    this.client.connect({
      onSuccess: () => {
        this._onConnect();
      },
      onFailure: () => {
        this._onConnectFailure();
      },
      willMessage: will,
      reconnect: true,
      keepAliveInterval: 10
    });
  }

  status_changed() {}
}

const formatDate = function(date) {
  return (
    date.getDate() +
    "-" +
    date.getMonth() +
    1 +
    "-" +
    date.getFullYear() +
    " " +
    date.getHours() +
    ":" +
    date.getMinutes() +
    ":" +
    date.getSeconds()
  );
};
module.exports = SccLib;
