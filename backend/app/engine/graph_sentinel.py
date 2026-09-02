import hashlib
import networkx as nx
from typing import List, Dict, Any, Tuple
from app.models.schemas import TransactionRequest, RiskFactor


class SybilGraphSentinel:
    """
    Graph-based fraud ring and Sybil network detector.
    Maintains a bipartite entity-relationship graph connecting:
    Customers <--> Devices <--> IPs <--> Delivery Addresses <--> Payment Instruments.
    
    Identifies tightly connected fraud clusters, promo-abuse syndicates,
    and distributed bot networks.
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.max_nodes = 10000

    def _hash_address(self, addr) -> str:
        s = f"{addr.line1.lower().strip()}_{addr.pincode.strip()}"
        return hashlib.md5(s.encode("utf-8")).hexdigest()[:10]

    def add_and_evaluate_transaction(self, txn: TransactionRequest) -> List[RiskFactor]:
        factors: List[RiskFactor] = []
        
        # Define entity node IDs with namespaces
        node_cust = f"cust:{txn.customer.customer_id}"
        node_device = f"dev:{txn.telemetry.device_fingerprint}"
        node_ip = f"ip:{txn.telemetry.ip_address}"
        node_addr = f"addr:{self._hash_address(txn.shipping_address)}"
        
        node_pay = None
        if txn.payment.payment_method == "card" and txn.payment.card_bin and txn.payment.card_last4:
            node_pay = f"card:{txn.payment.card_bin}_{txn.payment.card_last4}"
        elif txn.payment.payment_method == "upi" and txn.payment.upi_vpa:
            node_pay = f"upi:{txn.payment.upi_vpa.lower()}"

        # Add nodes with types
        self.graph.add_node(node_cust, type="customer", label=txn.customer.name)
        self.graph.add_node(node_device, type="device", label=txn.telemetry.device_fingerprint[:8])
        self.graph.add_node(node_ip, type="ip", label=txn.telemetry.ip_address)
        self.graph.add_node(node_addr, type="address", label=txn.shipping_address.city)
        if node_pay:
            self.graph.add_node(node_pay, type="payment", label=txn.payment.payment_method)

        # Add edges representing shared linkage
        self.graph.add_edge(node_cust, node_device, relation="uses_device")
        self.graph.add_edge(node_cust, node_ip, relation="from_ip")
        self.graph.add_edge(node_cust, node_addr, relation="ships_to")
        if node_pay:
            self.graph.add_edge(node_cust, node_pay, relation="pays_with")

        # Analyze subgraph / connected component around this customer
        if self.graph.has_node(node_cust):
            # Extract 2-hop ego network
            subgraph = nx.ego_graph(self.graph, node_cust, radius=2)
            num_nodes = subgraph.number_of_nodes()
            num_edges = subgraph.number_of_edges()

            # Count distinct customer accounts in this 2-hop cluster
            linked_customers = [n for n in subgraph.nodes() if n.startswith("cust:") and n != node_cust]
            linked_cards = [n for n in subgraph.nodes() if n.startswith("card:") or n.startswith("upi:")]
            linked_devices = [n for n in subgraph.nodes() if n.startswith("dev:")]

            if len(linked_customers) >= 3:
                severity = "critical" if len(linked_customers) >= 5 else "high"
                score = min(45.0, 20.0 + len(linked_customers) * 5.0)
                factors.append(RiskFactor(
                    name="Sybil Abuse-Ring Cluster Detected",
                    category="graph_sybil",
                    impact_score=score,
                    severity=severity,
                    description=(
                        f"Customer belongs to a dense graph ring connecting {len(linked_customers) + 1} "
                        f"accounts sharing {len(linked_devices)} devices and {len(linked_cards)} payment instruments"
                    ),
                    evidence={
                        "linked_accounts_count": len(linked_customers) + 1,
                        "cluster_node_count": num_nodes,
                        "cluster_edge_count": num_edges,
                        "shared_entities": {
                            "devices": len(linked_devices),
                            "payment_methods": len(linked_cards)
                        }
                    }
                ))

        # Node cap management to prevent memory leak
        if self.graph.number_of_nodes() > self.max_nodes:
            # Remove oldest 10% nodes
            nodes_to_remove = list(self.graph.nodes())[:1000]
            self.graph.remove_nodes_from(nodes_to_remove)

        return factors

    def get_graph_summary(self) -> Dict[str, Any]:
        """Returns statistics for dashboard threat radar."""
        components = list(nx.connected_components(self.graph))
        large_rings = [c for c in components if len([n for n in c if n.startswith("cust:")]) >= 3]
        return {
            "total_entities": self.graph.number_of_nodes(),
            "total_links": self.graph.number_of_edges(),
            "active_fraud_rings_count": len(large_rings),
            "largest_ring_size": max([len(c) for c in components]) if components else 0
        }


# Global singleton instance
graph_sentinel = SybilGraphSentinel()
