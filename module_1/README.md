# Chapter 1
In this chapter we are going to learn more about graphs, how to use different tools like, chains, routers, how to create agents, how to mantain memory of the conversations, and a little intro about how to deploy them 

## Motivation
When we use a language model normally these models are pretty simple in the context of what they can do or what can they access.
But we can provide them with tools, that can help to improve the things that can do, and work even a little bit better and do multistep proccess
and the best its that the models can select the tools that are going to be use depending the query of the user

## Graph

To create a new graph we have to start from the node 1, this node is then connected to other nodes, but always we have to start from node 1 and then go from there, the connection between them is called edges.

## Chains
With the chain we can add more information to pass it to the model, like a conversation, but also one cool thing that we can do is to add tools to the model, these tools will be integrating more things to do