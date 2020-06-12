import dfedForest
f = dfedForest.dfedForest()
f.forestPath = "garden"
f.loadForest()
f.load_dataset("treeData/randomData90.csv")
#f.load_dataset("treeData/v2randomData90.csv")
#f.load_dataset("datasets/iot-data/DataCSV/labeledmirai1-ack.csv")
#f.load_dataset("mirai.csv")

for i in range(len(f.forestList)):
    f.setMetrics(f.label,f.forestList[i].predict(f.data))
    f.getMetrics()

print "\n\t forest \t\n"
f.getClass(f.data)
f.classification
f.setMetrics(f.label,f.classification)    
f.getMetrics()
#f.load_dataset("treeData/v2randomData90.csv")
#f.saveTree(f.newTree)
#f.getClass(f.data)
#f.classification
#f.setMetrics(f.label,f.classification)    
#f.getMetrics()
f.queryTree("37df625190e29cc810665560c272c7de9349bbb6b07576ac9c23dcba8cf65a6a","query.txt")

f.setMetrics(f.label,f.forestList[100].predict(f.data))
f.getMetrics()
f.getClass(f.data)
f.classification
f.setMetrics(f.label,f.classification)    
f.getMetrics()
