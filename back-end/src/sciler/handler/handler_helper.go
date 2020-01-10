package handler

import (
	"encoding/json"
	"fmt"
	"github.com/sirupsen/logrus"
	"reflect"
	"sciler/config"
	"time"
)

// SendSetup sends the general set-up information to the front-end.
// This includes the name, all hints and event descriptions
// Statuses are also sent
func (handler *Handler) SendSetup() {
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "setup",
		Contents: map[string]interface{}{
			"name":    handler.Config.General.Name,
			"hints":   handler.getHints(),
			"events":  handler.getEventDescriptions(),
			"cameras": handler.getCameras(),
		},
	}
	jsonMessage, _ := json.Marshal(&message)
	handler.Communicator.Publish("front-end", string(jsonMessage), 3)
	logrus.Info("published setup data to front-end")
	handler.sendStatus("general")
	for _, value := range handler.Config.Devices {
		handler.sendStatus(value.ID)
		handler.GetStatus(value.ID)
	}
	handler.sendEventStatus()
}

// SendComponentInstruction sends a list of instructions to a client
func (handler *Handler) SendComponentInstruction(clientID string, instructions []config.ComponentInstruction) {
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "instruction",
		Contents: instructions,
	}
	jsonMessage, _ := json.Marshal(&message)
	logrus.Infof("sending instruction data to %s: %s", clientID, fmt.Sprint(message.Contents))
	handler.Communicator.Publish(clientID, string(jsonMessage), 3)
}

// SendInstruction sends a list of instructions to a client
func (handler *Handler) SendInstruction(clientID string, instructions []map[string]string) {
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "instruction",
		Contents: instructions,
	}
	jsonMessage, _ := json.Marshal(&message)
	logrus.Infof("sending instruction data to %s: %s", clientID, fmt.Sprint(message.Contents))
	handler.Communicator.Publish(clientID, string(jsonMessage), 3)
}

// updateStatus is the function to process status messages.
func (handler *Handler) updateStatus(raw Message) {
	contents := raw.Contents.(map[string]interface{})
	if device, ok := handler.Config.Devices[raw.DeviceID]; ok {
		logrus.Info("status message received from: " + raw.DeviceID + ", status: " + fmt.Sprint(raw.Contents))
		for k, v := range contents {
			err := handler.checkStatusType(*device, v, k)
			if err != nil {
				logrus.Error(err)
			} else {
				handler.Config.Devices[raw.DeviceID].Status[k] = v
			}
		}
	} else {
		logrus.Error("status message received from device ", raw.DeviceID, ", which is not in the config")
	}
}

// sendStatus sends all status and connection data of a device to the front-end.
// Information retrieved from config.
func (handler *Handler) sendStatus(deviceID string) {
	var message Message
	if device, ok := handler.Config.Devices[deviceID]; ok {
		message = Message{
			DeviceID: "back-end",
			TimeSent: time.Now().Format("02-01-2006 15:04:05"),
			Type:     "status",
			Contents: map[string]interface{}{
				"id":         device.ID,
				"status":     device.Status,
				"connection": device.Connection,
			},
		}
	} else if timer, ok2 := handler.Config.Timers[deviceID]; ok2 {
		duration, _ := timer.GetTimeLeft()
		message = Message{
			DeviceID: "back-end",
			TimeSent: time.Now().Format("02-01-2006 15:04:05"),
			Type:     "time",
			Contents: map[string]interface{}{
				"id":       timer.ID,
				"duration": duration.Milliseconds(),
				"state":    timer.State,
			},
		}
	} else {
		logrus.Errorf("error occurred while sending status of %s, since it is not recognised as a device or timer", deviceID)
		return
	}
	jsonMessage, _ := json.Marshal(&message)
	logrus.Info("sending status data to front-end: " + fmt.Sprint(message.Contents))
	handler.Communicator.Publish("front-end", string(jsonMessage), 3)
}

// HandleEvent is a function that checks and possible executes all rules according to the given (device/rule/timer) id
func (handler *Handler) HandleEvent(id string) {
	if rules, ok := handler.Config.StatusMap[id]; ok {
		for _, rule := range rules {
			if rule.Executed < rule.Limit && rule.Conditions.Resolve(handler.Config) {
				rule.Execute(handler)
			}
		}
	}
}

// sendEventStatus sends the status of events to the front-end
func (handler *Handler) sendEventStatus() {
	status := handler.getEventStatus()
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "event status",
		Contents: status,
	}
	jsonMessage, _ := json.Marshal(&message)
	logrus.Info("sending event status to front-end")
	handler.Communicator.Publish("front-end", string(jsonMessage), 3)
}

// getEventStatus returns json list with json objects with keys ["id", "status"]
// status is json object with key ruleName and value true (if executed == limit) or false
func (handler *Handler) getEventStatus() []map[string]interface{} {
	var list []map[string]interface{}
	for _, rule := range handler.Config.RuleMap {
		var status = make(map[string]interface{})
		status["id"] = rule.ID
		status["status"] = rule.Finished()
		list = append(list, status)
	}
	return list
}

// getHints returns map of hints with puzzle name as key and list of hints for that puzzle as value
func (handler *Handler) getHints() map[string][]string {
	hints := make(map[string][]string)
	for _, puzzle := range handler.Config.Puzzles {
		hints[puzzle.Event.Name] = puzzle.Hints
	}
	return hints
}

// getEventDescriptions returns map of hints with puzzle name as key and list of hints for that puzzle as value
func (handler *Handler) getEventDescriptions() map[string]string {
	events := make(map[string]string)
	for _, rule := range handler.Config.RuleMap {
		events[rule.ID] = rule.Description
	}
	return events
}

// getCameras returns map with camera name and camera link
func (handler *Handler) getCameras() []map[string]string {
	var cameras []map[string]string
	for _, camera := range handler.Config.Cameras {
		result := make(map[string]string)
		result["name"] = camera.Name
		result["link"] = camera.Link
		cameras = append(cameras, result)
	}
	return cameras
}

// GetStatus asks devices to send status
func (handler *Handler) GetStatus(deviceID string) {
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "instruction",
		Contents: []map[string]interface{}{
			{"instruction": "status update"},
		},
	}
	jsonMessage, _ := json.Marshal(&message)
	logrus.Info("sending status request to client computer: ", deviceID, fmt.Sprint(message.Contents))
	handler.Communicator.Publish(deviceID, string(jsonMessage), 3)
}

// SetTimer starts given timer
func (handler *Handler) SetTimer(timerID string, instructions config.ComponentInstruction) {
	switch instructions.Instruction {
	case "start":
		handler.Config.Timers[timerID].Start(handler)
	case "pause":
		handler.Config.Timers[timerID].Pause()
	case "add": // TODO: implement timer Add
	case "subtract": // TODO: implement timer subtract
	case "stop":
		handler.Config.Timers[timerID].Stop()
	default:
		logrus.Warnf("error occurred while reading timer instruction message: %v", instructions.Instruction)
	}
	handler.sendStatus(timerID)
}

// ProcessConfig reads the config in.
// If action is "check" then the return message must contain the possible errors
// If action is "use" then the message must tell the config a new config is now used and put it to use
func (handler *Handler) ProcessConfig(configToRead interface{}, action string) {
	jsonBytes, err := json.Marshal(configToRead)
	if err != nil {
		logrus.Error(err)
	}
	newConfig, errorList := config.ReadJSON(jsonBytes)
	message := Message{
		DeviceID: "back-end",
		TimeSent: time.Now().Format("02-01-2006 15:04:05"),
		Type:     "config",
		Contents: map[string][]string{},
	}
	if action == "check" {
		message.Contents = map[string][]string{"errors": errorList}
	}
	if action == "use" && len(errorList) == 0 {
		message.Type = "new config"
		handler.Config = newConfig
	}
	jsonMessage, _ := json.Marshal(&message)
	handler.Communicator.Publish("front-end", string(jsonMessage), 3)
}

// compareType compares a reflect.Kind and a string type and returns an error if not the same
func compareType(valueType reflect.Kind, inputType string) error {
	switch inputType {
	case "string":
		{
			if valueType != reflect.String {
				return fmt.Errorf("status type string expected but %s found as type", valueType.String())
			}
		}
	case "boolean":
		{
			if valueType != reflect.Bool {
				return fmt.Errorf("status type boolean expected but %s found as type", valueType.String())
			}
		}
	case "numeric":
		{
			if valueType != reflect.Int && valueType != reflect.Float64 {
				return fmt.Errorf("status type numeric expected but %s found as type", valueType.String())
			}
		}
	case "array":
		{
			if valueType != reflect.Slice {
				return fmt.Errorf("status type array/slice expected but %s found as type", valueType.String())
			}
		}
	default:
		// todo custom types
		return fmt.Errorf("custom types like: %s, are not yet implemented", inputType)
	}
	return nil
}

// checkStatusType checks if the type of the status change is correct for the component
func (handler *Handler) checkStatusType(device config.Device, status interface{}, component string) error {
	valueType := reflect.TypeOf(status).Kind()
	if inputType, ok := device.Input[component]; ok {
		if err := compareType(valueType, inputType); err != nil {
			return fmt.Errorf("%v with status %v for component %s", err, status, component)
		}
	} else if output, ok2 := device.Output[component]; ok2 {
		if err := compareType(valueType, output.Type); err != nil {
			return fmt.Errorf("%v with status %v for component %s", err, status, component)
		}
	} else {
		return fmt.Errorf("status message received from component %s, which is not in the config under device %s", component, device.ID)
	}
	return nil
}

func getMapSlice(input interface{}) ([]map[string]interface{}, error) {
	bytes, _ := json.Marshal(input)
	var output []map[string]interface{} // dirty trick to go from interface{} to []map[string]interface{}
	err := json.Unmarshal(bytes, &output)
	if err != nil {
		return nil, err
	}
	return output, nil
}
