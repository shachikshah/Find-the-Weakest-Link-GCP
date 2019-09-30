import networkx as nx
import random
import requests
from networkx.readwrite import json_graph
import aiohttp
from threading import Thread
import asyncio


class Vulnerability:
    def __init__(self):
        self.cve_id = self.get_id()
        self.exploit_probablity = 0
        self.exploit_cost = 0
        self.exploit_time = 0
        # 1 for start and 2 for end 0 for rest
        self.node_type = 0

    def get_id(self):
        return 'CVE-' + str(random.randint(2000, 2019)) + '-' + str('%04d' % random.randint(1, 1000))

    def get_score(self):
        # Take this score from mongodb data
        api_url = 'https://cve.circl.lu/api/cve/'+self.cve_id
        try:
            response = requests.get(api_url).json()
            score = float(response['cvss'])
            return score
        except:
            return (random.randint(1, 10)/10)

    def get_cost(self):
        return random.randint(10, 1000)

    def get_exp_time(self):
        return random.randint(1, 10)


def create_graph():
    # network dimensions
    m = random.randint(5, 8)
    n = random.randint(5, 8)

    network = nx.grid_2d_graph(m, n)

    # network = nx.minimum_spanning_tree(Grid)

    for node in network.nodes:
        network.nodes[node]['data'] = Vulnerability().__dict__

    # set target node
    network.nodes[(m - 1, n - 1)]['data']['node_type'] = 2
    network.nodes[(0, 0)]['data']['node_type'] = 1

    return network


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_requests())


def main():
    for i in range(20):
        new_loop = asyncio.new_event_loop()
        t = Thread(target=start_loop, args=(new_loop,))
        t.start()


async def send_requests():
    url = 'http://34.74.235.85/'
    data = json_graph.node_link_data(create_graph())

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            data = await response.text()
            print(data)


if __name__ == '__main__':
   main()
