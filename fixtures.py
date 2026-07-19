"""A day of invented traffic across six invented shipments."""

SHIPMENTS = {
    "SHP-101": {"status": "IN_TRANSIT", "lane": "Jebel Ali -> Riyadh"},
    "SHP-102": {"status": "AT_PICKUP", "lane": "Dammam -> Dubai"},
    "SHP-103": {"status": "ASSIGNED", "lane": "Jeddah -> NEOM"},
    "SHP-104": {"status": "LOADED", "lane": "Sharjah -> Muscat"},
    "SHP-105": {"status": "IN_TRANSIT", "lane": "Abu Dhabi -> Doha"},
    "SHP-106": {"status": "AT_DELIVERY", "lane": "Dubai -> Riyadh"},
}

MESSAGES = [
    {"id": "M01", "channel": "voice", "body": "SHP-104 left jebel ali gate now"},
    {"id": "M02", "channel": "ocr", "body": "SHP-102 delivery note stamped, 12 pallets"},
    {"id": "M03", "channel": "text", "body": "SHP-106 offloaded, unloading done"},
    {"id": "M04", "channel": "voice", "body": "boss SHP-105 reaching soon inshallah"},
    {"id": "M05", "channel": "text", "body": "SHP-101 loaded"},                      # illegal: already IN_TRANSIT
    {"id": "M06", "channel": "text", "body": "SHP-103 reached the pickup warehouse"},
    {"id": "M07", "channel": "voice", "body": "salam boss traffic very bad today"},
    {"id": "M08", "channel": "ocr", "body": "SHP-106 POD uploaded, receiver signed"},
    {"id": "M09", "channel": "text", "body": "SHP-104 on the way"},                  # duplicate after M01
    {"id": "M10", "channel": "text", "body": "ok boss thanks"},
    {"id": "M11", "channel": "voice", "body": "SHP-103 loading complete now leaving"},
    {"id": "M12", "channel": "text", "body": "SHP-102 departed"},
    {"id": "M13", "channel": "voice", "body": "truck reached delivery SHP-105"},
    {"id": "M14", "channel": "text", "body": "invoice for last week please"},
    {"id": "M15", "channel": "ocr", "body": "weighbridge slip attached"},            # no shipment id
    {"id": "M16", "channel": "text", "body": "SHP-101 at the receiver now"},
    {"id": "M17", "channel": "voice", "body": "SHP-999 delivered"},                  # unknown shipment
    {"id": "M18", "channel": "text", "body": "SHP-105 delivered, offloaded"},
    {"id": "M19", "channel": "voice", "body": "almost there SHP-102"},
    {"id": "M20", "channel": "text", "body": "SHP-101 delivered"},
]
