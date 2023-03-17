import Decimal from "decimal.js";
import {ClientMessage} from "./ClientMessages";
import {ServerMessage} from "./ServerMessages";

export interface Envelope {
    messageType: ClientMessage | ServerMessage
    message: object
}

export interface Message {

}

export interface Quote {
    bid: Decimal
    offer: Decimal
    minAmount: Decimal
    maxAmount: Decimal
}
