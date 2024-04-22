import json
import re
from enum import Enum
from typing import Dict, List, Optional, Union

import certifi
import grpc
from cosmpy.aerial.contract import LedgerContract
from cosmpy.protos.cosmos.base.query.v1beta1.pagination_pb2 import PageRequest
from cosmpy.protos.cosmos.tx.v1beta1.service_pb2 import GetTxsEventRequest
from cosmpy.protos.cosmos.tx.v1beta1.service_pb2_grpc import ServiceStub as TxGrpcClient


class ActionType(Enum):
    """
    Enumeration representing the types of actions that can be associated with an event.
    """

    REFUND = "refund"
    TRANSFER = "transfer"
    PARTIAL_TRANSFER = "partial_transfer"
    CREATE = "create"


class Event:
    """
    Class representing an event in the blockchain.
    """

    def __init__(
        self,
        id: str,
        txn_hash: str,
        action: ActionType,
        from_address: str,
        to_address: str,
        amount: str,
        trade_pair: str,
        sell_price: str,
        escrow_address: str,
        remaining_amount: Optional[str] = None,
        preferred_agent: Optional[str] = None,
        match_others: Optional[bool] = True
    ):
        """
        Initialize an event object.

        :param id: Identifier for the event.
        :param txn_hash: Transaction hash of the event.
        :param action: ActionType representing the action performed in this event.
        :param from_address: Address of the sender.
        :param to_address: Address of the receiver.
        :param amount: Amount transferred.
        :param trade_pair: Trading pair.
        :param sell_price: Selling price.
        :param escrow_address: Escrow Address.
        :param remaining_amount: Remaining amount (optional).
        :param preferred_agent: Preferred Agent Address (optional).
        :param match_others: Preferred Match Others (optional).
        
        """
        self.id = id
        self.txn_hash = txn_hash
        self.action = action
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.trade_pair = trade_pair
        self.sell_price = sell_price
        self.escrow_address = escrow_address
        self.remaining_amount = remaining_amount
        self.preferred_agent = preferred_agent
        self.match_others = match_others

    @classmethod
    def from_dict(cls, event_dict: Dict[str, Union[str, int]]) -> "Event":
        """
        Create an Event instance from a dictionary.

        :param event_dict: Dictionary containing event information.
        :return: Event instance.
        """
        txn_hash = event_dict["TxnHash"]
        action = event_dict.get("action") or event_dict.get("action1")
        from_address = event_dict.get("from") or event_dict.get("from1")
        to_address = event_dict.get("to") or event_dict.get("to1")
        amount = event_dict.get("amount") or event_dict.get("amount1")
        id = event_dict.get("id") or event_dict.get("id1")
        trade_pair = cls.extract_trade_pair(id)
        sell_price = event_dict.get("sell_price") or event_dict.get("sell_price1")
        escrow_address = event_dict.get("escrow_contract_address")
        remaining_amount = event_dict.get("remaining_amount") or event_dict.get(
            "remaining_amount1"
        )
        preferred_agent = event_dict.get("preferred_agent") or event_dict.get(
            "preferred_agent1"
        )
        match_others = event_dict.get("match_others") or event_dict.get(
            "match_others1"
        )

        return cls(
            id,
            txn_hash,
            action,
            from_address,
            to_address,
            amount,
            trade_pair,
            sell_price,
            escrow_address,
            remaining_amount,
            preferred_agent,
            match_others
        )

    def extract_trade_pair(id: str) -> str:
        """
        Extract trade pair from the event id.

        :param id: Identifier for the event.
        :return: Trade pair extracted from the id.
        """
        trade_pair = re.match(r"([A-Za-z/]+)", id).group(1)
        return trade_pair

    def __str__(self) -> str:
        """
        String representation of the Event instance.

        :return: String representing the event.
        """
        return (
            f"Id: {self.id}\n"
            f"Transaction Hash: {self.txn_hash}\n"
            f"Action: {self.action}\n"
            f"From Address: {self.from_address}\n"
            f"To Address: {self.to_address}\n"
            f"Amount: {self.amount}\n"
            f"Trade Pair: {self.trade_pair}\n"
            f"Sell Price: {self.sell_price}\n"
            f"Escrow Address: {self.escrow_address}\n"
            f"Remaining Amount: {self.remaining_amount}\n"
            f"Preferred Agent: {self.preferred_agent}\n"
            f"Match Others: {self.match_others}"
        )


class EventRetriever:
    """
    Class responsible for fetching events from the blockchain.
    """

    def __init__(
        self, contract_address: str, grpc_url: str, file_name: str = "processsed_events"
    ):
        """
        Initialize the EventRetriever instance.

        :param contract_address: Address of the smart contract to fetch events from.
        :param grpc_url: URL of the gRPC server.
        :param file_name: Name of the file to store processed events (optional).
        """
        self.contract_address = contract_address
        self.grpc_url = grpc_url
        self.processed_events = set()
        self.processed_events_file = file_name + ".json"
        self.txs = None
        
    def _get_grpc_client(self):
            # Connect to gRPC server
            with open(certifi.where(), "rb") as f:
                trusted_certs = f.read()
                credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
                grpc_client = grpc.secure_channel(self.grpc_url, credentials)
                return grpc_client

    def load_processed_events(self, discard_processed_events: bool):
        """
        Load processed events from a file if they are not discarded.

        :param discard_processed_events: Flag indicating whether to discard processed events.
        """
        if discard_processed_events:
            try:
                with open(self.processed_events_file, "r") as f:
                    self.processed_events = set(json.load(f))
            except FileNotFoundError:
                pass

    def fetch_events(
        self,
        discard_processed_events: bool,
        action_type: Optional[Union[ActionType, List[ActionType]]] = None,
        user_wallet_address: Optional[str] = None,
    ) -> List[Event]:
        """
        Fetch events from the blockchain based on certain filters.

        :param discard_processed_events: Flag indicating whether to discard processed events.
        :param action_type: ActionType or list of ActionTypes to filter by (optional).
        :param user_wallet_address: User wallet address to filter by (optional).
        :return: List of filtered events.
        """
        self.load_processed_events(discard_processed_events)
        grpc_client = self._get_grpc_client()
        txs = TxGrpcClient(grpc_client)

        wasm_action = None  # Wasm action events to be filtered, None means all events
        txn_events = self._get_events(txs, self.contract_address, wasm_action)
        events_to_send = [
            event
            for event in self._filter_events(
                txn_events, action_type, user_wallet_address
            )
            if event.txn_hash not in self.processed_events
        ]
        if discard_processed_events:
            self.processed_events.update(event.txn_hash for event in events_to_send)
            with open(self.processed_events_file, "w") as f:
                json.dump(list(self.processed_events), f)
        return events_to_send

    def _query_txs_events(self, txs, queries: List[str]) -> List[Dict]:
        """
        Query transaction events with pagination.

        :param txs: Transaction gRPC client.
        :param queries: List of queries to search for.
        :return: List of dictionaries representing transaction events.
        """
        offset = 0
        res = []

        while True:
            tx_res = txs.GetTxsEvent(
                GetTxsEventRequest(
                    events=queries, pagination=PageRequest(offset=offset)
                )
            )
            res += tx_res.tx_responses

            offset += len(tx_res.tx_responses)

            if offset >= tx_res.pagination.total:
                break

        return res

    def _get_events(
        self, txs, contract_address, wasm_action: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve events associated with a contract.

        :param txs: Transaction gRPC client.
        :param contract_address: Address of the contract to fetch events from.
        :param wasm_action: Specific wasm action to filter by (optional).
        :return: List of dictionaries representing transaction events.
        """
        queries = [f"execute._contract_address='{contract_address}'"]
        if wasm_action is not None:
            queries.append(f"wasm.action='{wasm_action}'")
        return self._query_txs_events(txs, queries)

    def _filter_events(
        self,
        resp,
        action_type: Optional[Union[ActionType, List[ActionType]]] = None,
        user_wallet_address: Optional[str] = None,
    ) -> List[Event]:
        """
        Filter the transaction events by action type and user wallet address.

        :param resp: List of transaction events.
        :param action_type: ActionType or list of ActionTypes to filter by (optional).
        :param user_wallet_address: User wallet address to filter by (optional).
        :return: List of filtered Event instances.
        """
        filtered_data = []
        action_types = []
        if isinstance(action_type, ActionType):
            action_types.append(action_type)
        elif isinstance(action_type, list):
            action_types.extend(action_type)

        for tx in resp:
            for obj in tx.logs:
                events = str(obj.events)
                json_events = (
                    events.replace("[", "")
                    .replace("]", "")
                    .replace("\n", "")
                    .replace("  ", "")
                    .split(",")
                )
                for event in json_events:
                    if 'type: "wasm"' in event:
                        item = event.replace('type: "wasm"', "").replace(
                            "attributes {", ""
                        )
                        pairs = item.split('key: "')[1:]
                        result = {"TxnHash": tx.txhash}
                        for pair in pairs:
                            key = pair.split('"')[0]
                            value = pair.split('"')[2]
                            if key == "_contract_address":
                                contract_count = len(result) - 1
                                key = (
                                    "cw20_contract_address"
                                    if contract_count == 0
                                    else "escrow_contract_address"
                                )
                                result[key] = value
                            else:
                                key_count = result.get(key, 0) + 1
                                key = f"{key}{key_count}"
                                result[key] = value
                        if action_type is not None:
                            if action_types and all(
                                result.get("action") != action.value
                                and result.get("action1") != action.value
                                for action in action_types
                            ):
                                continue
                        if user_wallet_address is not None and (
                            result.get("from") != user_wallet_address
                            and result.get("from1") != user_wallet_address
                        ):
                            continue
                        filtered_data.append(Event.from_dict(result))
        return filtered_data
