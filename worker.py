import random
from networkx.readwrite import json_graph
import os
from google.cloud import pubsub_v1
import time
import json
import os.path
import bucket_operations
# import google.cloud.pubsub_v1.types
# import google.cloud.pubsub_v1.policy.thread
# import concurrent.futures

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

project_id = 'striped-impulse-239003'
topic_name = 'cve-search-topic'
subscription_name = "cve-search"


def callback_sub(message):
    # print('Received message: {}'.format(message))
    data = message.data
    print('Processing: '+str(message.message_id))
    data = json.loads(data)
    msg_id = message.message_id
    graph_from_json(data, msg_id)
    time.sleep(5)
    message.ack()


def subscribe():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    flow_control = pubsub_v1.types.FlowControl(max_messages=2)
    subscriber.subscribe(subscription_path, callback=callback_sub, flow_control=flow_control)

    print('Listening for messages on {}'.format(subscription_path))

    # keep this method alive to receive response from callback
    while True:
        time.sleep(60)




def get_score(cve_id):
    
    return (random.randint(1, 10) / 10)


def get_cost():
    return random.randint(50, 1000)


def get_exp_time():
    return random.randint(1, 10)


def graph_from_json(data, msg_id):
    # pickup the data form QUEUE
    network = json_graph.node_link_graph(data)
    # nx.draw(network)
    # plt.show()

    for node in network.nodes:
        cve_id = network.nodes[node]['data']['cve_id']
        network.nodes[node]['data']['exploit_probablity'] = get_score(cve_id)
        network.nodes[node]['data']['exploit_cost'] = get_cost()
        network.nodes[node]['data']['exploit_time'] = get_exp_time()
        network.nodes[node]['data']['heuristic'] = get_heurisitc_cost(list(network.nodes)[-1], node) * 10

    all_nodes = list(network.nodes)
    # publish this result to s3
    result = a_star(network, all_nodes[0], all_nodes[-1])

    write_result(result, msg_id)


# returns manhattan distance b/w two nodes
def get_heurisitc_cost(t1, t2):
    x = abs(t1[0] - t2[0])
    y = abs(t1[1] - t2[1])
    return x + y


def a_star(network, curr_node, target):
    visited = list()
    open_paths = dict()
    open_paths[curr_node] = (network.nodes[curr_node]['data']['exploit_cost'],
                             network.nodes[curr_node]['data']['heuristic'],
                             curr_node)
    print('searching target..')
    while open_paths:
        # get next minimum open path and set curr_node
        lcp, values = min(open_paths.items(), key=lambda x: x[1][0] + x[1][1])
        cost_so_far, heuristic, curr_node = values

        for neighbor in network.neighbors(curr_node):
            if str(neighbor) not in lcp:
                new_path = str(lcp) + '->' + str(neighbor)
                cost_so_far = cost_so_far + network.nodes[neighbor]['data']['exploit_cost']
                heuristic = network.nodes[neighbor]['data']['heuristic']
                open_paths[new_path] = (cost_so_far, heuristic, neighbor)

        visited.append(curr_node)
        # print(lcp)
        del open_paths[lcp]

        if curr_node == target:
            # print('target_found')
            result, values = min(open_paths.items(), key=lambda x: x[1][0] + x[1][1])
            # print(result, values)
            return str(result)+' '+str(values)


def write_result(output, msg_id):
    print('writing result')
    # print(result, values)
    save_path = os.getcwd()+'/outputs/'
    path_name = os.path.join(save_path, msg_id + ".txt")
    text_file = open(path_name, 'w')
    print(output, msg_id)
    text_file.write(output)
    text_file.close()

    dest = msg_id + ".txt"
    bucket_operations.uploadToBucket(dest, path_name)
    print('Uploaded')
    return


subscribe()
