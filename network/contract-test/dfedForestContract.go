package main

import (
	"bytes"
	"fmt"
	"strconv"
	"strings"
	"time"
    "encoding/json"
    "github.com/golang-collections/go-datastructures/queue"
    "github.com/hyperledger/fabric-chaincode-go/shim"
    pb "github.com/hyperledger/fabric-protos-go/peer"
)

type SimpleChaincode struct{
}

// Define transaction structures
type AdvertisementTransaction struct{
	TxId string                 `json:"TxId"`
	TxType string				`json:"TxType"`
    Tree string					`json:"Tree"`
    OrgID string                `json:"OrgID"`
    TxIndex string              `json:"TxIndex"`
	//publicKey byte[]			`json:"pk"`
}

// Define client (org) structure
type Client struct{
	//publicKey byte[]			`json:"pk"`i
	Assets string  				`json:"Assets"`
	OrgID string				`json:"OrgID"`
	//publicKey byte[]			`json:"pk"`i
}


// Initialize queue of pending transactions

func main() {
	err := shim.Start(new(SimpleChaincode))
	if err != nil {
		fmt.Printf("Error starting Simple Chaincode: %s", err)
	}
}

// Initialize the smart contract with 2 organizations and their respective assets
func (t *SimpleChaincode) Init(stub shim.ChaincodeStubInterface) pb.Response {
    return shim.Success(nil)
}

// Define invocable functions on the smart contract
func (t *SimpleChaincode) Invoke(stub shim.ChaincodeStubInterface) pb.Response {
	function, args := stub.GetFunctionAndParameters()

	if function == "issueAdvertisement" {
		return t.issueAdvertisement(stub, args)
	} else if function == "getHistoryForTransaction" {
		return t.getHistoryForTransaction(stub, args)
	}

	return shim.Error("Received unknown function invocation")
}

// Issue a new advertisement transaction on the blockchain
func (t *SimpleChaincode) issueAdvertisement (stub shim.ChaincodeStubInterface, args []string) pb.Response{

	var err error

	if len(args) != 2 {
		return shim.Error("Incorrect number of arguments. Expected 2 arguments. Usage: '{\"Args\":[\"<Tree>\",\"<OrgID>\"]}'")
	}

	if len(args[0]) <= 0 {
		return shim.Error("1st argument must be a non-empty string")
	}
	if len(args[1]) <= 0 {
		return shim.Error("2nd argument must be a non-empty string")
	}

    txID := stub.GetTxID()
    txType := "advertisement"
	tree := args[0]
	orgID := args[1]


	// Check if transaction already exists in the blockchain
	contractAsBytes, err := stub.GetState(txID)
	if err != nil {
		return shim.Error("Failed to get contract: " + err.Error())
	} else if contractAsBytes != nil {
		fmt.Println("This txID already exists: " + txID)
		return shim.Error("This contract already exists: " + txID)
	}

    // Create JSON to be stored in the global state
    contractJSONasString := `{"TxID": "` + txID + `","txType": "` + txType + `","tree": "` + tree + `","orgID": "` + orgID + `"}`
	contractJSONasBytes:= []byte(contractJSONasString)

	// Save transaction to global state
	err = stub.PutState(txID, contractJSONasBytes)
	if err != nil {
		return shim.Error(err.Error())
	}

	return shim.Success([]byte(txID))
}


// Track a transaction history by its txID
func (t *SimpleChaincode) getHistoryForTransaction(stub shim.ChaincodeStubInterface, args []string) pb.Response {

	if len(args) < 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	txID := args[0]

    // Retrieve transaction history
	resultsIterator, err := stub.GetHistoryForKey(txID)
	if err != nil {
		return shim.Error(err.Error())
	}
	defer resultsIterator.Close()

	// Format results as a JSON array containing historic values for the the transaction
	var buffer bytes.Buffer
	buffer.WriteString("[")

	bArrayMemberAlreadyWritten := false
	for resultsIterator.HasNext() {
		response, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(err.Error())
		}
		// Add a comma before array members, suppress it for the first array member
		if bArrayMemberAlreadyWritten == true {
			buffer.WriteString(",")
		}
		buffer.WriteString("{\"TxId\":")
		buffer.WriteString("\"")
		buffer.WriteString(response.TxId)
		buffer.WriteString("\"")

		buffer.WriteString(", \"Value\":")
		// if it was a delete operation on given key, then we need to set the
		//corresponding value null. Else, we will write the response.Value
		//as-is (as the Value itself a JSON marble)
		if response.IsDelete {
			buffer.WriteString("null")
		} else {
			buffer.WriteString(string(response.Value))
		}

		buffer.WriteString(", \"Timestamp\":")
		buffer.WriteString("\"")
		buffer.WriteString(time.Unix(response.Timestamp.Seconds, int64(response.Timestamp.Nanos)).String())
		buffer.WriteString("\"")

		buffer.WriteString(", \"IsDelete\":")
		buffer.WriteString("\"")
		buffer.WriteString(strconv.FormatBool(response.IsDelete))
		buffer.WriteString("\"")

		buffer.WriteString("}")
		bArrayMemberAlreadyWritten = true
	}
	buffer.WriteString("]")

	return shim.Success(buffer.Bytes())
}


