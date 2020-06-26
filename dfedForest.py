from pickle import dumps
from pickle import dump
from pickle import loads
from os import listdir
from os import system
from random import randint
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
import base64
import sys



class dfedForest(object):
    # not finished
    def __init__(self,forestList=[],forestPath="treeModels",tiebreaker=0,minervaTree=0,data=[],label=[]):
        
        # Path to load trees
        self.forestPath = forestPath
        
        # List of all trees on the forest
        self.forestList = forestList
    
        # Load all trees
        self.loadForest()
            
        # Number of the trees on the forest
        self.forestDensity = len(self.forestList)              
        
        # Output of the model
        self.classification = []
        
        # Path to save trees
        self.seedPath = "garden"
        
        # Metrics of the classification
        self.metricsList = [0,0,0,0]    

        # Tiebreaker criteria: 0 always negative; 1 always positive; 2 random; 3 minervaTree vote
        self.tiebreaker = tiebreaker

        # ID of the minervaTree on the list
        self.minervaTree = minervaTree
   
        # Dataset
        self.data = data

        # Original label of dataset
        self.label = label

    def load_dataset(self,fileName):
        self.data = []
        self.label = []
        with open(fileName, "r") as readData:
            for line in readData:
                self.data.append(line.split(",")[5:-1])
                self.label.append(line[-2:-1])

    # Update the list of trees with the models on treesPath directory
    def loadForest(self):
        self.forestList = []
        allTrees = listdir(self.forestPath) 
        for name in allTrees:
            with open(self.forestPath+"/"+name, "rb") as readFile:
                self.forestList.append(loads(readFile.read()))            
 
    # Generate a new tree based on a dataset
    def createTree(self,depth):
        self.newTree = tree.DecisionTreeClassifier(max_depth=depth)
        self.newTree = self.newTree.fit(self.data, self.label)
        
    def createRandomTree(self,depth):
        self.newRandomTree = RandomForestClassifier(n_estimators=1,max_depth=depth)
        self.newRandomTree = self.newRandomTree.fit(self.data, self.label)
    
    # Show all tree on the list
    def getTrees(self):
        for tree in self.forestList:
            print(tree)

    # Update classification metrics
    def setMetrics(self, original_label,classification):
        FP = 0.0
        FN = 0.0
        TP = 0.0
        TN = 0.0
        for index in range(len(original_label)):
            # True classification cases
            if(float(original_label[index]) == float(classification[index])):
                if(float(original_label[index]) == 1.0):
                    TP += 1
                else:
                    TN += 1
            # False classification cases
            else:
                if(float(classification[index]) == 1.0):
                    FP += 1
                else:
                    FN += 1
        #if TP != 0 or TN != 0:
        self.metricsList[1] = TP/(TP+FP)
        #if TP != 0 or FN != 0:
        self.metricsList[2] = TP/(TP+FN)
        #if TP != 0 or FN != 0 or TP != 0 or TN != 0:
        self.metricsList[0] = (TP+TN)/(TP+TN+FP+FN)
        #if self.metricsList[1] != 0 or self.metricsList[2] != 0:
        self.metricsList[3] = (2*self.metricsList[1]*self.metricsList[2])/(self.metricsList[1]+self.metricsList[2])
        print (TP,TN,FP,FN)            

    # Show the current metrics of a classification
    def getMetrics(self):
        print("Acc: "+str(self.metricsList[0])+" Prec: "+str(self.metricsList[1])+" Rec: "+str(self.metricsList[2])+" F1: "+str(self.metricsList[3])+"\n")

    # publish the tree on the blockchain
    def publishTree(self,newTree):
        new = base64.b64encode(dumps(newTree))
        cmd = "docker exec cli peer chaincode invoke -n mycc -o orderer.example.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc -c \'{\"Args\":[\"issueAdvertisement\",\"SeiLa\",\"Dados de Sensores IoT\",\"10\",\"IoT\",\"10.0.0.1\",\""+new+"\"]}\'"
        system(cmd)

    def queryTree(self,tx, fileToSave):
        system("docker exec -it cli peer chaincode invoke -n mycc -o orderer.example.com:7050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n mycc -c \'{\"Args\":[\"getHistoryForTransaction\",\""+tx+"\"]}\' > "+fileToSave)
        transaction = open(fileToSave,"r").readline()
        newTree = loads(base64.b64decode(transaction.split("\\\"")[37]))
        self.forestList.append(newTree)


    # Remove a tree from the forestList
    def removeTree(self,treeID):
        self.forestList.remove(treeID)

    # Add a tree on the forestList
    def addTree(self,newTree):
        self.forestList.append(newTree)

    # Save a given tree on a binary file
    def saveTree(self,newTree):
        save = dumps(newTree)
        with open(self.seedPath+"/tree"+str(len(listdir("garden"))+1),"wb") as writer:
            writer.write(save)

    # Classify a flow
    def getClass(self,flow):
        votes = []
        # Get the votes of all trees in the forest 
        for model in self.forestList:
            votes.append(model.predict(flow))
        
        voteCompute = []    
        for entry in votes[0]:
        # voteCompute[n] all votes for flow n where -> x = positive votes , y = negatives votes
        #                       x,y
            voteCompute.append([0,0])           

        # Compute all votes
        for index in range(len(votes[0])):
            for member in votes:
                if int(member[index]) == 1:
                    voteCompute[index][0] += 1
                else:
                    voteCompute[index][1] += 1
        # Classify each flow
        index = 0
        for entry in voteCompute:
            if entry[0] > entry[1]:
                self.classification.append(1)
            elif entry[0] < entry[1]:
                self.classification.append(0)
            else:
                # always classify as negative if have a tie
                if self.tiebreaker == 0:
                    self.classification.append(0)
                # always classify as positive if have a tie
                elif self.tiebreaker == 1:
                    self.classification.append(1)
                # random classification if have a tie
                elif self.tiebreaker == 2:
                    self.classification.append(randint(0,1))
                # minerva tree classification if have a tie
                elif self.tiebreaker == 3:
                    self.classification.append(vote[minervaTree][index])
            index += 1
            
        
if __name__ == "__main__":
    f = dfedForest()
    for index in range(1,len(listdir("treeData"))+1):
        f.load_dataset("treeData/randomData"+str(index)+".csv")
        f.createTree()
        f.saveTree(f.newTree)
