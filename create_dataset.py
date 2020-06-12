from random import randint


#                 string   string    int
def randomDataset(dataset, output, samples):
    with open(output,"w") as write:
        writer = []
        with open(dataset,"r") as read:
            all_lines = read.readlines()
            for index in range(samples):
                writer.append(all_lines[randint(0,len(all_lines)-1)])
            write.writelines(writer)



for index in range(1,101):
    randomDataset("mirai.csv","treeData/randomData"+str(index)+".csv",1000)
