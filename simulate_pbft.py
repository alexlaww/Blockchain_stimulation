import random
import time
import numpy as np
import matplotlib.pyplot as plt


class Node:
    def __init__(self, is_byzantine=False):
        self.is_byzantine = is_byzantine

    def vote(self, transaction):
        # Simulate latency
        latency = self.simulate_latency()
        time.sleep(latency)

        if self.is_byzantine:
            return random.choice([True, False])  # Byzantine node: random behavior
        else:
            return True  # Honest node: always approves

    def simulate_latency(self):
        if self.is_byzantine:
            return random.uniform(0.05, 0.2)  # Byzantine nodes slower
        else:
            return random.uniform(0.01, 0.05)  # Honest nodes faster


class PBFTProtocol:
    def __init__(self, nodes):
        self.nodes = nodes

    def consensus(self, transaction):
        votes = [node.vote(transaction) for node in self.nodes]
        approved_votes = sum(votes)
        if approved_votes >= (2/3) * len(self.nodes):
            return True
        else:
            return False


class CEPBFTProtocol:
    def __init__(self, nodes):
        self.nodes = nodes
        self.trusted_nodes = self.classify_nodes()

    def classify_nodes(self):
        # Trust only honest nodes
        return [node for node in self.nodes if not node.is_byzantine]

    def consensus(self, transaction):
        if len(self.trusted_nodes) == 0:
            return False
        votes = [node.vote(transaction) for node in self.trusted_nodes]
        approved_votes = sum(votes)
        if approved_votes >= (2/3) * len(self.trusted_nodes):
            return True
        else:
            return False


def simulate(protocol_class, n_nodes=20, byzantine_ratio=0.2, n_transactions=100):
    nodes = []
    n_byzantine = int(n_nodes * byzantine_ratio)
    for _ in range(n_byzantine):
        nodes.append(Node(is_byzantine=True))
    for _ in range(n_nodes - n_byzantine):
        nodes.append(Node(is_byzantine=False))
    random.shuffle(nodes)

    protocol = protocol_class(nodes)

    correct_transactions = 0
    start_time = time.time()

    for _ in range(n_transactions):
        transaction = {}  # Dummy transaction
        if protocol.consensus(transaction):
            correct_transactions += 1

    elapsed_time = time.time() - start_time
    throughput = correct_transactions / elapsed_time  # transactions per second

    return throughput, correct_transactions, n_transactions


# Parameters
n_nodes = 20
n_transactions = 100
byzantine_ratios = [0.0, 0.1, 0.2, 0.3, 0.4]

pbft_throughputs = []
cepbft_throughputs = []
pbft_correct_ratios = []
cepbft_correct_ratios = []

for ratio in byzantine_ratios:
    pbft_tp, pbft_correct, pbft_total = simulate(PBFTProtocol, n_nodes, ratio, n_transactions)
    cepbft_tp, cepbft_correct, cepbft_total = simulate(CEPBFTProtocol, n_nodes, ratio, n_transactions)

    pbft_throughputs.append(pbft_tp)
    cepbft_throughputs.append(cepbft_tp)

    pbft_correct_ratios.append(pbft_correct / pbft_total)
    cepbft_correct_ratios.append(cepbft_correct / cepbft_total)


# Plot Throughput
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(byzantine_ratios, pbft_throughputs, 'r-o', label='PBFT')
plt.plot(byzantine_ratios, cepbft_throughputs, 'b-o', label='CE-PBFT')
plt.xlabel('Byzantine Node Ratio')
plt.ylabel('Throughput (transactions/sec)')
plt.title('Throughput vs Byzantine Ratio (with Latency)')
plt.legend()
plt.grid(True)

# Plot Fault Tolerance
plt.subplot(1, 2, 2)
plt.plot(byzantine_ratios, pbft_correct_ratios, 'r-s', label='PBFT')
plt.plot(byzantine_ratios, cepbft_correct_ratios, 'b-s', label='CE-PBFT')
plt.xlabel('Byzantine Node Ratio')
plt.ylabel('Correct Transaction Ratio')
plt.title('Fault Tolerance vs Byzantine Ratio')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Final Results
print("\n==== Final Results ====")
for i, ratio in enumerate(byzantine_ratios):
    print(f"Byzantine Ratio {ratio*100:.0f}%:")
    print(f" PBFT    -> Throughput: {pbft_throughputs[i]:.2f} tx/sec, Correct: {pbft_correct_ratios[i]*100:.1f}%")
    print(f" CE-PBFT -> Throughput: {cepbft_throughputs[i]:.2f} tx/sec, Correct: {cepbft_correct_ratios[i]*100:.1f}%")
